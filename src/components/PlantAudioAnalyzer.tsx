'use client';

import { useState, type FormEvent } from 'react';
import { AudioLines, Upload } from 'lucide-react';

type Analysis = {
  status?: string;
  event_count?: number;
  plant_id?: string;
  sample_rate_hz?: number;
  duration_ms?: number;
  samples?: number;
  rms?: number;
  aggregation?: string;
  event_votes?: Record<string, number>;
  classification_available?: boolean;
  classification?: string | null;
  scores?: Record<string, number> | null;
  model_cv_event_macro_f1?: number;
  model_cv_plant_macro_f1?: number;
  evaluation_mode?: 'held_out_source_plant' | 'unseen_plant_not_validated';
  note?: string;
  error?: string;
};

export function PlantAudioAnalyzer() {
  const [species, setSpecies] = useState<'tomato' | 'tobacco'>('tomato');
  const [files, setFiles] = useState<File[]>([]);
  const [confirmPlantRecording, setConfirmPlantRecording] = useState(false);
  const [result, setResult] = useState<Analysis | null>(null);
  const [busy, setBusy] = useState(false);

  async function analyze(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!files.length || !confirmPlantRecording) return;
    setBusy(true);
    setResult(null);
    const body = new FormData();
    files.forEach((file) => body.append('audio', file));
    body.set('species', species);
    body.set('plant_recording', 'true');
    try {
      const response = await fetch('/api/analyze', { method: 'POST', body });
      const data = await response.json() as Analysis;
      setResult(data);
    } catch {
      setResult({ error: 'Could not reach the local analysis service.' });
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="rounded-xl border border-sage-200 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-2">
        <AudioLines className="h-4 w-4 text-sage-600" />
        <h2 className="text-lg font-semibold text-sage-800">Inspect one plant’s ultrasonic events</h2>
      </div>
      <p className="mt-1 text-sm leading-6 text-sage-500">
        Select the event WAVs for one plant from the PlantSounds archive. Filenames must share the same plant ID. The API accepts mono 2 ms, 500 kHz events; longer 22.05 kHz recordings are not silently resampled or classified.
      </p>
      <form onSubmit={analyze} className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-end">
        <label className="flex-1 text-sm font-medium text-sage-700">
          Event WAV
          <input type="file" multiple accept=".wav,audio/wav" onChange={(event) => { setFiles(Array.from(event.target.files ?? [])); setResult(null); }} className="mt-1 block w-full rounded-lg border border-sage-200 p-2 text-sm file:mr-3 file:rounded-md file:border-0 file:bg-sage-100 file:px-3 file:py-1.5 file:text-sage-700" />
        </label>
        <label className="text-sm font-medium text-sage-700">
          Species model
          <select value={species} onChange={(event) => setSpecies(event.target.value as 'tomato' | 'tobacco')} className="mt-1 block w-full rounded-lg border border-sage-200 bg-white px-3 py-2">
            <option value="tomato">Tomato</option>
            <option value="tobacco">Tobacco</option>
          </select>
        </label>
        <button type="submit" disabled={!files.length || !confirmPlantRecording || busy} className="inline-flex items-center justify-center gap-2 rounded-lg bg-sage-700 px-4 py-2.5 text-sm font-medium text-white hover:bg-sage-800 disabled:cursor-not-allowed disabled:opacity-50">
          <Upload className="h-4 w-4" />{busy ? 'Inspecting…' : 'Inspect locally'}
        </button>
      </form>
      <label className="mt-3 flex items-start gap-2 text-xs leading-5 text-sage-600">
        <input type="checkbox" checked={confirmPlantRecording} onChange={(event) => setConfirmPlantRecording(event.target.checked)} className="mt-1" />
        I confirm these are plant-emission recordings, not empty-pot or greenhouse-noise controls.
      </label>
      <p className="mt-2 text-xs leading-5 text-sage-500">Use multiple events from the same plant when available. Source plant IDs in the development set use the fold model that held that plant out; new IDs use a full-data model and are unvalidated.</p>
      {result && <div className={`mt-4 rounded-lg p-4 text-sm ${result.error ? 'bg-rose-50 text-rose-800' : 'bg-sage-50 text-sage-800'}`} aria-live="polite">
        {result.error ? <p>{result.error}</p> : <>
          <p className="font-semibold">{result.classification_available ? `Experimental plant-level class: ${result.classification}` : 'Signal inspection complete; classification model unavailable'}</p>
          <p className="mt-1">Plant ID {result.plant_id} · {result.event_count} events analyzed</p>
          {result.evaluation_mode && <p className="mt-1">Inference set: {result.evaluation_mode === 'held_out_source_plant' ? 'held-out source plant (fold model)' : 'unseen plant (full-data model; external validation absent)'}</p>}
          {result.event_votes && <p className="mt-1">Event votes: {Object.entries(result.event_votes).map(([label, count]) => `${label}: ${count}`).join(' · ')}</p>}
          {result.scores && <p className="mt-1">Raw model scores (uncalibrated): {Object.entries(result.scores).map(([label, score]) => `${label}: ${(100 * score).toFixed(1)}%`).join(' · ')}</p>}
          {typeof result.model_cv_event_macro_f1 === 'number' && <p className="mt-1">Exploratory plant-grouped CV macro-F1: {(100 * result.model_cv_event_macro_f1).toFixed(1)}% at event level · {(100 * (result.model_cv_plant_macro_f1 ?? 0)).toFixed(1)}% after plant aggregation</p>}
          <p className="mt-2 text-xs leading-5">{result.note}</p>
        </>}
      </div>}
    </section>
  );
}
