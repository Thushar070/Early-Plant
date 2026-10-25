import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { tmpdir } from 'node:os';
import { basename, join, resolve } from 'node:path';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';

export const runtime = 'nodejs';

function runAnalysis(wavPaths: string[], species: string): Promise<string> {
  const projectRoot = process.cwd();
  const scriptPath = resolve(projectRoot, 'ml/src/predict_plantsounds.py');
  const executable = process.env.PLANTSENSE_PYTHON || 'python3';
  return new Promise((resolvePromise, reject) => {
    const child = spawn(executable, [scriptPath, '--wav', ...wavPaths, '--species', species], { cwd: projectRoot });
    let stdout = '';
    let stderr = '';
    const timeout = setTimeout(() => child.kill('SIGKILL'), 15_000);
    child.stdout.setEncoding('utf8');
    child.stderr.setEncoding('utf8');
    child.stdout.on('data', (chunk: string) => { stdout += chunk; });
    child.stderr.on('data', (chunk: string) => { stderr += chunk; });
    child.on('error', reject);
    child.on('close', (code) => {
      clearTimeout(timeout);
      if (code === 0) resolvePromise(stdout);
      else reject(new Error(stderr.slice(-2000) || `Audio analysis exited with code ${code}`));
    });
  });
}

export async function POST(request: Request) {
  let tempDirectory: string | undefined;
  try {
    const contentLength = Number(request.headers.get('content-length') || 0);
    if (contentLength > 20_100_000) {
      return Response.json({ error: 'The uploaded event files must total under 20 MB.' }, { status: 413 });
    }
    const form = await request.formData();
    const audioFiles = form.getAll('audio');
    const species = form.get('species');
    const plantRecording = form.get('plant_recording');
    if (audioFiles.length < 1 || audioFiles.length > 200 || audioFiles.some((audio) => !(audio instanceof File)) || (species !== 'tomato' && species !== 'tobacco')) {
      return Response.json({ error: 'Provide 1–200 event WAV files and choose tomato or tobacco.' }, { status: 400 });
    }
    if (plantRecording !== 'true') {
      return Response.json({ error: 'Confirm that these are plant-emission recordings, not empty-pot or greenhouse-noise controls.' }, { status: 400 });
    }
    const files = audioFiles as File[];
    if (files.some((audio) => audio.size < 44 || audio.size > 2_000_000) || files.reduce((sum, file) => sum + file.size, 0) > 20_000_000) {
      return Response.json({ error: 'Each WAV must be under 2 MB and all files together under 20 MB.' }, { status: 413 });
    }
    const names = files.map((file) => basename(file.name));
    const identities = names.map((name) => /^id_(\d+)_sound_(\d+)\.wav$/i.exec(name));
    if (identities.some((match) => !match) || new Set(identities.map((match) => match?.[1])).size !== 1 || new Set(identities.map((match) => match?.[2])).size !== names.length) {
      return Response.json({ error: 'Use PlantSounds event filenames with one shared id_<plant_id> and unique sound IDs.' }, { status: 400 });
    }
    tempDirectory = await mkdtemp(join(tmpdir(), `plantsense-${randomUUID()}-`));
    const wavPaths: string[] = [];
    for (let index = 0; index < files.length; index += 1) {
      const audio = files[index];
      const bytes = Buffer.from(await audio.arrayBuffer());
      if (bytes.toString('ascii', 0, 4) !== 'RIFF' || bytes.toString('ascii', 8, 12) !== 'WAVE') {
        return Response.json({ error: `Invalid RIFF/WAVE file: ${names[index]}` }, { status: 415 });
      }
      const wavPath = join(tempDirectory, names[index]);
      await writeFile(wavPath, bytes, { flag: 'wx' });
      wavPaths.push(wavPath);
    }
    const output = await runAnalysis(wavPaths, species);
    return Response.json(JSON.parse(output));
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unable to inspect this recording.';
    return Response.json({ error: message }, { status: 422 });
  } finally {
    if (tempDirectory) await rm(tempDirectory, { recursive: true, force: true });
  }
}
