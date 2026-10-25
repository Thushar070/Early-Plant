import csv
import importlib.util
import json
import pathlib
import random
import sys
import tempfile
import unittest
import wave


ML_SRC = pathlib.Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(ML_SRC))

from config import CLASSES, ID_TO_LABEL, LABEL_TO_ID, label_to_id, validate_label_id
from panns_utils import load_audio_tagging, unwrap_panns_model
from reproducibility import seed_everything
from split_validation import assert_no_group_overlap, assert_no_path_overlap
from training_utils import update_best_metric


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]


class LabelMappingTests(unittest.TestCase):
    def test_five_class_mapping_is_contiguous_and_bidirectional(self):
        self.assertEqual(len(CLASSES), 5)
        self.assertEqual(list(LABEL_TO_ID.values()), [0, 1, 2, 3, 4])
        for label, class_id in LABEL_TO_ID.items():
            self.assertEqual(label_to_id(label), class_id)
            self.assertEqual(ID_TO_LABEL[class_id], label)
            self.assertEqual(validate_label_id(str(class_id)), class_id)

    def test_unknown_labels_and_out_of_range_or_fractional_ids_are_rejected(self):
        for invalid in ("Unknown Stress", "", None):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                label_to_id(invalid)
        for invalid in ("-1", "5", "1.2", 1.2, -1, 5, True):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                validate_label_id(invalid)


class SplitTests(unittest.TestCase):
    def test_existing_csv_paths_do_not_overlap(self):
        paths_by_split = {}
        for split in ("train", "val", "test"):
            with (PROJECT_ROOT / f"{split}.csv").open(newline="", encoding="utf-8") as handle:
                paths_by_split[split] = [row["audio_path"] for row in csv.DictReader(handle)]
        assert_no_path_overlap(paths_by_split)

    def test_existing_csv_labels_match_shared_label_mapping(self):
        for split in ("train", "val", "test"):
            with (PROJECT_ROOT / f"{split}.csv").open(newline="", encoding="utf-8") as handle:
                for row in csv.DictReader(handle):
                    self.assertEqual(label_to_id(row["label"]), validate_label_id(row["label_id"]))

    def test_existing_class_counts_match_manifest(self):
        manifest = json.loads((PROJECT_ROOT / "ml/split_manifest.json").read_text())
        for split, filename in (("train", "train.csv"), ("validation", "val.csv"), ("test", "test.csv")):
            with (PROJECT_ROOT / filename).open(newline="", encoding="utf-8") as handle:
                counts = {}
                for row in csv.DictReader(handle):
                    counts[row["label"]] = counts.get(row["label"], 0) + 1
            self.assertEqual(counts, manifest["class_counts"][split])

    def test_path_overlap_is_detected(self):
        with self.assertRaisesRegex(ValueError, "path overlap"):
            assert_no_path_overlap({"train": ["a.wav"], "val": ["a.wav"]})
        with self.assertRaisesRegex(ValueError, "duplicated path"):
            assert_no_path_overlap({"train": ["a.wav", "a.wav"], "val": ["b.wav"]})

    def test_group_overlap_is_detected_when_groups_are_supplied(self):
        with self.assertRaisesRegex(ValueError, "group overlap"):
            assert_no_group_overlap({"train": ["plant-1"], "test": ["plant-1"]})
        assert_no_group_overlap({"train": ["plant-1"], "test": ["plant-2"]})


class CheckpointSelectionTests(unittest.TestCase):
    def test_improvement_updates_metric_for_both_checkpoint_metadata_and_selection(self):
        is_best, saved_best_metric = update_best_metric(0.31, 0.28)
        self.assertTrue(is_best)
        self.assertEqual(saved_best_metric, 0.31)

    def test_tie_or_regression_preserves_prior_best_metric(self):
        for metric in (0.28, 0.20):
            with self.subTest(metric=metric):
                is_best, saved_best_metric = update_best_metric(metric, 0.28)
                self.assertFalse(is_best)
                self.assertEqual(saved_best_metric, 0.28)


class ReproducibilityTests(unittest.TestCase):
    def test_python_and_numpy_rngs_repeat_for_the_same_seed(self):
        import numpy as np

        seed_everything(123)
        first = (random.random(), np.random.random())
        seed_everything(123)
        second = (random.random(), np.random.random())
        self.assertEqual(first, second)


class PannsDeviceTests(unittest.TestCase):
    def test_detected_device_is_forwarded_and_initialization_failure_is_clear(self):
        calls = []

        class FakeAudioTagging:
            def __init__(self, device):
                calls.append(device)
                self.model = object()

        load_audio_tagging("cpu", FakeAudioTagging, cuda_available=False)
        self.assertEqual(calls, ["cpu"])

        class FailingAudioTagging:
            def __init__(self, device):
                raise ValueError("unsupported by test double")

        with self.assertRaisesRegex(RuntimeError, "could not initialize on cpu"):
            load_audio_tagging("cpu", FailingAudioTagging, cuda_available=False)

    def test_cuda_unavailable_and_unsupported_devices_fail_early(self):
        with self.assertRaisesRegex(RuntimeError, "CUDA is unavailable"):
            load_audio_tagging("cuda", lambda **kwargs: None, cuda_available=False)
        with self.assertRaisesRegex(ValueError, "only CPU or CUDA"):
            load_audio_tagging("mps", lambda **kwargs: None, cuda_available=False)

    def test_wrapping_is_optional(self):
        class Wrapped:
            module = "base-model"

        class Unwrapped:
            pass

        self.assertEqual(unwrap_panns_model(type("Tag", (), {"model": Wrapped()})()), "base-model")
        unwrapped = Unwrapped()
        self.assertIs(unwrap_panns_model(type("Tag", (), {"model": unwrapped})()), unwrapped)


@unittest.skipUnless(
    importlib.util.find_spec("torch")
    and importlib.util.find_spec("torchaudio")
    and importlib.util.find_spec("librosa"),
    "audio shape check requires the project's PyTorch, torchaudio, and librosa dependencies",
)
class AudioPreprocessingTests(unittest.TestCase):
    def test_two_second_mono_wav_has_expected_log_mel_tensor_shape(self):
        import math
        import struct
        from preprocessing import prepare_audio
        from config import SAMPLE_RATE

        with tempfile.TemporaryDirectory() as temp_dir:
            path = pathlib.Path(temp_dir) / "two_seconds.wav"
            frames = bytearray()
            for index in range(SAMPLE_RATE * 2):
                sample = int(0.2 * 32767 * math.sin(2 * math.pi * 440 * index / SAMPLE_RATE))
                frames.extend(struct.pack("<h", sample))
            with wave.open(str(path), "wb") as output:
                output.setnchannels(1)
                output.setsampwidth(2)
                output.setframerate(SAMPLE_RATE)
                output.writeframes(frames)

            tensor = prepare_audio(str(path))
            self.assertEqual(tuple(tensor.shape), (1, 128, 87))


@unittest.skipUnless(importlib.util.find_spec("sklearn"), "metric check requires scikit-learn")
class MetricTests(unittest.TestCase):
    def test_known_multiclass_example_metrics(self):
        from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

        targets = [0, 1, 2, 2]
        predictions = [0, 2, 2, 1]
        self.assertAlmostEqual(accuracy_score(targets, predictions), 0.5)
        self.assertAlmostEqual(precision_score(targets, predictions, average="macro", zero_division=0), 0.5)
        self.assertAlmostEqual(recall_score(targets, predictions, average="macro", zero_division=0), 0.5)
        self.assertAlmostEqual(f1_score(targets, predictions, average="macro", zero_division=0), 0.5)


if __name__ == "__main__":
    unittest.main()
