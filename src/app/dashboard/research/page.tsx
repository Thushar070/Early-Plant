import type { ReactNode } from 'react';
import { AlertTriangle, AudioLines, BookOpen, FlaskConical, Gauge, Microscope } from 'lucide-react';
import { PlantAudioAnalyzer } from '@/components/PlantAudioAnalyzer';
import report from '../../../../ml/experiments/cpu_baseline_20261025/report.json';
import tomatoRun from '../../../../ml/models/plantsounds/tomato_dry_vs_cut_20261025_161052_utc/report.json';
import tobaccoRun from '../../../../ml/models/plantsounds/tobacco_dry_vs_cut_20261025_161111_utc/report.json';

const metrics = report.selected_model_validation;

function percent(value: number) {
  return `${(value * 100).toFixed(1)}%`;
}

export default function ResearchPage() {
  return (
    <div className="space-y-6">
      <header className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-sage-100">
          <FlaskConical className="h-5 w-5 text-sage-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-sage-800">Research prototype</h1>
          <p className="text-sm text-sage-500">Evidence, experiment results, and what needs validating next</p>
        </div>
      </header>

      <section className="rounded-xl border border-amber-300 bg-amber-50 p-5" role="status">
        <div className="flex items-start gap-3">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-700" />
          <div>
            <h2 className="font-semibold text-amber-950">Research only — no validated plant-health diagnosis</h2>
            <p className="mt-1 text-sm leading-6 text-amber-900">
              A source-backed experiment can distinguish some dry vs. cut recordings in plant-grouped cross-validation. The legacy five-class model is near chance and is not used here; results do not validate health decisions or live field monitoring.
            </p>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3" aria-label="Dataset facts">
        <Fact icon={<AudioLines className="h-5 w-5" />} label="Public source events" value="5,477 × 2 ms" detail="Mono WAV, 500,000 samples/second" />
        <Fact icon={<Gauge className="h-5 w-5" />} label="Plant groups" value="107 tomato · 63 tobacco" detail="Separate plant-ID groups within species" />
        <Fact icon={<Microscope className="h-5 w-5" />} label="Classification scope" value="Dry vs. cut" detail="Separate within tomato and tobacco" />
      </section>

      <section className="rounded-xl border border-sage-200 bg-white p-5 shadow-sm">
        <div className="flex items-center gap-2">
          <FlaskConical className="h-4 w-4 text-sage-600" />
          <h2 className="text-lg font-semibold text-sage-800">Dry vs. cut, grouped by plant</h2>
        </div>
        <p className="mt-1 text-sm leading-6 text-sage-500">
          Five-fold stratified cross-validation keeps every plant in exactly one validation fold. Scores below aggregate each plant’s held-out sound-event predictions by majority vote. These folds were reused while adjusting model weighting, so treat them as exploratory—not independent confirmation.
        </p>
        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          {[
            { label: 'Tomato', run: tomatoRun, artifact: 'tomato_dry_vs_cut_20261025_161052_utc' },
            { label: 'Tobacco', run: tobaccoRun, artifact: 'tobacco_dry_vs_cut_20261025_161111_utc' },
          ].map(({ label, run, artifact }) => (
            <div key={label} className="rounded-lg border border-sage-100 p-4">
              <div className="flex items-baseline justify-between gap-3">
                <h3 className="font-semibold text-sage-800">{label}</h3>
                <span className="text-xs text-sage-500">{run.n_unique_plants} plants · {run.n_events.toLocaleString()} events</span>
              </div>
              <div className="mt-3 grid grid-cols-2 gap-3">
                <Metric label="Plant accuracy" value={percent(run.plant_level_out_of_fold_metrics.accuracy)} />
                <Metric label="Plant macro-F1" value={percent(run.plant_level_out_of_fold_metrics.macro_f1)} />
              </div>
              <p className="mt-3 text-xs leading-5 text-sage-500">
                95% plant-bootstrap CI for macro-F1: {percent(run.plant_level_out_of_fold_metrics.bootstrap_95_ci.intervals.macro_f1[0])}–{percent(run.plant_level_out_of_fold_metrics.bootstrap_95_ci.intervals.macro_f1[1])}. Plant-level majority baseline macro-F1: {percent(run.plant_level_majority_baseline.macro_f1)}.
              </p>
              <p className="mt-1 text-xs text-sage-500">Event-level macro-F1: {percent(run.out_of_fold_metrics.macro_f1)}</p>
          <p className="mt-1 text-xs text-sage-400">Checkpoints: <code>ml/models/plantsounds/{artifact}/model.joblib</code> and its held-out fold models</p>
            </div>
          ))}
        </div>
        <p className="mt-4 text-xs leading-5 text-sage-500">
          This evaluates source-condition discrimination—not healthy-vs-stressed diagnosis. Event-level performance is lower than plant-level aggregation. These internal grouped cross-validation results are exploratory because model weighting was iterated on the same plant cohorts; the bootstrap intervals do not correct for that selection. The source README provides no session IDs. Model scores are not calibrated confidence.
        </p>
      </section>

      <section className="rounded-xl border border-sage-200 bg-white p-5 shadow-sm">
        <div className="flex items-center gap-2">
          <FlaskConical className="h-4 w-4 text-sage-600" />
          <h2 className="text-lg font-semibold text-sage-800">Legacy five-class diagnostic (not used for these predictions)</h2>
        </div>
        <p className="mt-1 text-sm text-sage-500">Log-spaced Welch spectral power features; model chosen by validation macro-F1.</p>
        <div className="mt-5 grid gap-3 sm:grid-cols-3">
          <Metric label="Validation accuracy" value={percent(metrics.accuracy)} />
          <Metric label="Validation macro-F1" value={percent(metrics.macro_f1)} />
          <Metric label="Validation balanced accuracy" value={percent(metrics.balanced_accuracy)} />
        </div>
        <div className="mt-4 rounded-lg bg-sage-50 p-4 text-sm leading-6 text-sage-700">
          Selected <strong>{report.selected_model.replaceAll('_', ' ')}</strong>. Five-class chance accuracy is 20%.
          The run used 700 training and 150 validation clips. It did not evaluate the test split.
          Earlier exploratory work already examined that split, so it is not a pristine final holdout.
          Training was not repeated on the validation set after model selection.
        </div>
        <div className="mt-5 overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-sage-200 text-xs uppercase tracking-wide text-sage-500">
              <tr><th className="py-2 pr-4">Candidate</th><th className="py-2 pr-4">Accuracy</th><th className="py-2 pr-4">Macro-F1</th><th className="py-2">Balanced accuracy</th></tr>
            </thead>
            <tbody>
              {report.validation_metrics.map((row) => <tr key={row.model} className="border-b border-sage-100 text-sage-700">
                <td className="py-2 pr-4 capitalize">{row.model.replaceAll('_', ' ')}</td>
                <td className="py-2 pr-4 tabular-nums">{percent(row.accuracy)}</td>
                <td className="py-2 pr-4 tabular-nums">{percent(row.macro_f1)}</td>
                <td className="py-2 tabular-nums">{percent(row.balanced_accuracy)}</td>
              </tr>)}
              <tr className="text-sage-500">
                <td className="py-2 pr-4">Historical CNN peak (different run)</td>
                <td className="py-2 pr-4 tabular-nums">27.3%</td>
                <td className="py-2 pr-4 tabular-nums">22.9%</td>
                <td className="py-2">—</td>
              </tr>
            </tbody>
          </table>
          <p className="mt-2 text-xs text-sage-400">Historical run is not directly comparable: it used a different model/training recipe and the original partitions lack verified group isolation.</p>
        </div>
        <p className="mt-3 text-xs text-sage-400">Run date: 25 October 2026 · Seed: 42 · Artifact: ml/experiments/cpu_baseline_20261025</p>
      </section>

      <PlantAudioAnalyzer />

      <section className="rounded-xl border border-sage-200 bg-white p-5 shadow-sm">
        <div className="flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-sage-600" />
          <h2 className="text-lg font-semibold text-sage-800">Research context</h2>
        </div>
        <p className="mt-2 text-sm leading-6 text-sage-600">
          Published plant-acoustics work reports signals under specific controlled conditions, but those findings do not
          validate general field performance. The preserved legacy 22.05 kHz dataset cannot capture ultrasonic frequencies above 11.025 kHz and lacks verified plant/session IDs. The separate Dryad source has README-derived plant IDs and supports the grouped experiment shown above, but provides no session identifiers.
        </p>
        <ul className="mt-4 space-y-2 text-sm">
          <li><a className="text-sage-700 underline decoration-sage-300 underline-offset-2" href="https://pubmed.ncbi.nlm.nih.gov/37001499/" target="_blank" rel="noreferrer">Khait et al. (2023), plant sounds under stress — PubMed</a></li>
          <li><a className="text-sage-700 underline decoration-sage-300 underline-offset-2" href="https://datadryad.org/dataset/doi:10.5061/dryad.jwstqjqf7" target="_blank" rel="noreferrer">Associated Dryad dataset and README</a></li>
          <li><a className="text-sage-700 underline decoration-sage-300 underline-offset-2" href="https://doi.org/10.1111/nph.19648" target="_blank" rel="noreferrer">Son et al. (2024), evidence and uncertainty — DOI</a></li>
          <li><a className="text-sage-700 underline decoration-sage-300 underline-offset-2" href="https://pubmed.ncbi.nlm.nih.gov/38345027/" target="_blank" rel="noreferrer">Plant ultrasound detection methods (2024) — PubMed</a></li>
        </ul>
        <p className="mt-4 text-xs text-sage-500">See the local <code>ml/RESEARCH.md</code> for the acquisition and evaluation plan.</p>
      </section>

      <section className="rounded-xl border border-sage-200 bg-white p-5 shadow-sm">
        <h2 className="text-lg font-semibold text-sage-800">Reproducible public-data workflow</h2>
        <p className="mt-2 text-sm leading-6 text-sage-600">
          The selected source is Dryad’s 2023 PlantSounds archive: 2 ms, 500 kHz tomato/tobacco events under dry or cut treatments, plus empty-pot and greenhouse-noise controls. This prototype narrows classification to dry-versus-cut within one species; it does not label healthy-versus-stressed plants.
        </p>
        <p className="mt-3 text-sm leading-6 text-sage-600">
          The supplied CC0 archive is safely unpacked under <code>datasets/public_plantsounds/</code>. To reproduce acquisition, run <code>python ml/src/prepare_plantsounds.py</code>; it creates <code>metadata.csv</code> and a template. The supplied README documents plant and per-plant sound IDs in the filenames; session IDs are not provided. Review the generated mapping before training, which requires at least five plants per condition for plant-grouped cross-validation.
        </p>
        <p className="mt-3 text-sm leading-6 text-sage-600">
          Run <code>python ml/src/train_plantsounds_baseline.py --species tomato</code> or use <code>--species tobacco</code> after reviewing the metadata. Evaluation keeps each plant wholly within one fold and saves a fold checkpoint for held-out-source inference. New plant IDs use the full-data model and are explicitly unvalidated. Results remain exploratory and are not a plant-health diagnosis.
        </p>
      </section>

      <section className="rounded-xl border border-sage-200 bg-white p-5 shadow-sm">
        <h2 className="text-lg font-semibold text-sage-800">What would make the next result stronger?</h2>
        <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm leading-6 text-sage-600">
          <li>Verify species, stress protocol, labels, sensor calibration, and independent physiological measurements.</li>
          <li>Collect calibrated recordings across the intended frequency band, with environmental and negative controls.</li>
          <li>Split evaluation by plant and recording session, then reserve a separate site or time cohort.</li>
          <li>Compare simple baselines and audio models on the same frozen protocol; report class-wise results and uncertainty.</li>
        </ol>
      </section>
    </div>
  );
}

function Fact({ icon, label, value, detail }: { icon: ReactNode; label: string; value: string; detail: string }) {
  return <div className="rounded-xl border border-sage-200 bg-white p-4 shadow-sm">
    <div className="flex items-center gap-2 text-sage-500">{icon}<span className="text-xs font-semibold uppercase tracking-wide">{label}</span></div>
    <p className="mt-3 text-lg font-semibold text-sage-800">{value}</p>
    <p className="mt-1 text-xs text-sage-500">{detail}</p>
  </div>;
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="rounded-lg border border-sage-100 bg-sage-50 p-4">
    <p className="text-xs font-medium uppercase tracking-wide text-sage-500">{label}</p>
    <p className="mt-1 text-2xl font-bold tabular-nums text-sage-800">{value}</p>
  </div>;
}
