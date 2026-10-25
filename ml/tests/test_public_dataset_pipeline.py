import csv
import io
import pathlib
import sys
import tempfile
import unittest
import zipfile


ML_SRC = pathlib.Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(ML_SRC))

from prepare_plantsounds import category_from_path, safe_extract
from train_plantsounds_baseline import feature_vector, feature_vector_rich, read_rows


class PublicDatasetPreparationTests(unittest.TestCase):
    def test_source_folder_mapping_uses_only_published_category_names(self):
        self.assertEqual(category_from_path(pathlib.Path("PlantSounds/Tomato Dry/event.wav")), ("tomato", "dry"))
        self.assertEqual(category_from_path(pathlib.Path("PlantSounds/Greenhouse Noises/event.wav")), ("unknown", "greenhouse_noise_control"))
        self.assertIsNone(category_from_path(pathlib.Path("invented_label/event.wav")))

    def test_filename_ids_follow_supplied_readme_contract(self):
        from prepare_plantsounds import parse_source_ids

        self.assertEqual(parse_source_ids("id_126_sound_23.wav"), ("126", "23"))
        with self.assertRaisesRegex(ValueError, "does not match"):
            parse_source_ids("invented_event.wav")

    def test_archive_paths_cannot_escape_the_extraction_directory(self):
        content = io.BytesIO()
        with zipfile.ZipFile(content, "w") as archive:
            archive.writestr("../outside.wav", b"not audio")
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(RuntimeError, "Unsafe archive path"):
                safe_extract(content.getvalue(), pathlib.Path(temporary) / "raw")
            self.assertFalse((pathlib.Path(temporary) / "outside.wav").exists())

    def test_training_requires_verified_plant_id_and_id_source_fields(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            metadata = root / "metadata.csv"
            with metadata.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["file_path", "species", "condition", "plant_id", "session_id", "id_source"])
                writer.writeheader()
                writer.writerow({"file_path": "event.wav", "species": "tomato", "condition": "dry"})
            with self.assertRaisesRegex(ValueError, "Missing verified plant_id"):
                read_rows(metadata, root, "tomato")

    def test_metadata_paths_cannot_escape_dataset_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            metadata = root / "metadata.csv"
            with metadata.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["file_path", "species", "condition", "plant_id", "session_id", "id_source"])
                writer.writeheader()
                writer.writerow({"file_path": "../event.wav", "species": "tomato", "condition": "dry", "plant_id": "p1", "session_id": "s1", "id_source": "original metadata"})
            with self.assertRaisesRegex(ValueError, "relative and confined"):
                read_rows(metadata, root, "tomato")


class PublicDatasetFeatureTests(unittest.TestCase):
    def test_wrong_sampling_rate_is_rejected_before_ultrasound_features(self):
        import numpy as np
        from scipy.io import wavfile

        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "ordinary_audio.wav"
            wavfile.write(path, 22_050, np.zeros(1000, dtype=np.int16))
            with self.assertRaisesRegex(ValueError, "Expected 500 kHz"):
                feature_vector(path)

    def test_rich_spectral_and_envelope_features_are_finite(self):
        import numpy as np
        from scipy.io import wavfile

        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "id_1_sound_1.wav"
            time = np.arange(1000) / 500_000
            signal = (0.2 * np.sin(2 * np.pi * 40_000 * time) * 32767).astype(np.int16)
            wavfile.write(path, 500_000, signal)
            features = feature_vector_rich(path)
            self.assertEqual(features.shape, (112,))
            self.assertTrue(np.isfinite(features).all())

    def test_valid_event_without_new_source_model_is_inspection_only(self):
        import numpy as np
        from unittest.mock import patch
        from scipy.io import wavfile
        from predict_plantsounds import analyze

        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "id_1_sound_1.wav"
            time = np.arange(1000) / 500_000
            signal = (0.2 * np.sin(2 * np.pi * 40_000 * time) * 32767).astype(np.int16)
            wavfile.write(path, 500_000, signal)
            with patch("predict_plantsounds.model_for_species", return_value=None):
                result = analyze([path], "tomato")
            self.assertEqual(result["status"], "analysis_only")
            self.assertFalse(result["classification_available"])
            self.assertIsNone(result["classification"])
            self.assertEqual(result["event_count"], 1)


if __name__ == "__main__":
    unittest.main()
