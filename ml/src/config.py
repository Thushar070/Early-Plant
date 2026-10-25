from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT_DIR / "datasets"
AUDIO_DIR = DATASET_DIR / "plant_sounds"
CSV_PATH = DATASET_DIR / "plant_stress_sound_dataset.csv"

SAMPLE_RATE = 22050

CLASSES = [
    "Drought",
    "Heat Stress",
    "Mechanical Damage",
    "Nutrient Deficiency",
    "Pest Infestation"
]

NUM_CLASSES = len(CLASSES)
SEED = 42

LABEL_TO_ID = {label: index for index, label in enumerate(CLASSES)}
ID_TO_LABEL = {index: label for label, index in LABEL_TO_ID.items()}


def label_to_id(label):
    """Map a known class label to its zero-based classifier target."""
    try:
        return LABEL_TO_ID[label]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"Unknown plant-stress label: {label!r}") from exc


def validate_label_id(value):
    """Return a valid integer target without silently truncating floats."""
    if isinstance(value, bool):
        raise ValueError(f"Invalid plant-stress label ID: {value!r}")
    if isinstance(value, str):
        if not value.isdecimal():
            raise ValueError(f"Invalid plant-stress label ID: {value!r}")
        value = int(value)
    else:
        try:
            value = value.__index__()
        except (AttributeError, TypeError):
            raise ValueError(f"Invalid plant-stress label ID: {value!r}") from None

    if not 0 <= value < NUM_CLASSES:
        raise ValueError(f"Plant-stress label ID must be in [0, {NUM_CLASSES - 1}], got {value}")
    return int(value)
