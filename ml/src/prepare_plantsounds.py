"""Acquire and safely unpack the public Dryad PlantSounds archive.

The script preserves the downloaded ZIP and does not invent plant/session IDs.
It generates an annotation template; training stays disabled until those IDs
are verified from source metadata.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "datasets" / "public_plantsounds"
DATASET_DOI = "10.5061/dryad.jwstqjqf7"
DOWNLOAD_URL = "https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.jwstqjqf7/download"
MAX_ARCHIVE_BYTES = 50_000_000
MAX_UNPACKED_BYTES = 500_000_000

SOURCE_CATEGORIES = {
    "tomato dry": ("tomato", "dry"),
    "tobacco dry": ("tobacco", "dry"),
    "tomato cut": ("tomato", "cut"),
    "tobacco cut": ("tobacco", "cut"),
    "empty pot": ("unknown", "empty_pot_control"),
    "greenhouse noises": ("unknown", "greenhouse_noise_control"),
}
FILENAME_ID = re.compile(r"id_(?P<record_id>\d+)_sound_(?P<sound_id>\d+)\.wav", re.IGNORECASE)


def category_from_path(path: Path) -> tuple[str, str] | None:
    for part in reversed(path.parts[:-1]):
        key = re.sub(r"\s+", " ", part.strip().lower())
        if key in SOURCE_CATEGORIES:
            return SOURCE_CATEGORIES[key]
    return None


def parse_source_ids(filename: str) -> tuple[str, str]:
    match = FILENAME_ID.fullmatch(Path(filename).name)
    if not match:
        raise ValueError(f"Filename does not match the source README's id_<plant_id>_sound_<sound_id> format: {filename}")
    return match.group("record_id"), match.group("sound_id")


def download_archive() -> bytes:
    request = urllib.request.Request(
        DOWNLOAD_URL,
        headers={"User-Agent": "PlantSense-Local-Research-Prototype/0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            if response.status != 200:
                raise RuntimeError(f"Dryad returned HTTP {response.status}")
            raw = response.read(MAX_ARCHIVE_BYTES + 1)
    except URLError as exc:
        raise RuntimeError(
            "Could not download the Dryad archive from this network. Download PlantSounds.zip "
            "from https://datadryad.org/dataset/doi:10.5061/dryad.jwstqjqf7 and rerun with --archive."
        ) from exc
    if len(raw) > MAX_ARCHIVE_BYTES:
        raise RuntimeError(f"Refusing archive larger than {MAX_ARCHIVE_BYTES} bytes")
    if not zipfile.is_zipfile(io.BytesIO(raw)):
        raise RuntimeError("Dryad response was not a ZIP archive; preserve it for inspection")
    return raw


def safe_extract(raw: bytes, destination: Path) -> list[Path]:
    destination_resolved = destination.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    files: list[Path] = []
    total_size = 0
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        members = archive.infolist()
        if len(members) > 100_000:
            raise RuntimeError("Archive contains an unreasonable number of entries")
        for info in members:
            rel = PurePosixPath(info.filename)
            if rel.is_absolute() or ".." in rel.parts:
                raise RuntimeError(f"Unsafe archive path: {info.filename}")
            # Ignore symlink entries rather than materializing links from the archive.
            if (info.external_attr >> 16) & 0o170000 == 0o120000:
                continue
            total_size += info.file_size
            if total_size > MAX_UNPACKED_BYTES:
                raise RuntimeError("Archive expands beyond the configured 500 MB safety limit")
            target = (destination / Path(*rel.parts)).resolve()
            if target != destination_resolved and destination_resolved not in target.parents:
                raise RuntimeError(f"Archive path escapes destination: {info.filename}")
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as src, target.open("xb") as dst:
                dst.write(src.read(MAX_UNPACKED_BYTES + 1))
            if target.suffix.lower() == ".wav":
                files.append(target)
    return files


def write_annotation_template(wav_paths: list[Path], extracted_root: Path, output: Path) -> int:
    rows = []
    for path in sorted(wav_paths):
        category = category_from_path(path.relative_to(extracted_root))
        if category is None:
            continue
        species, condition = category
        record_id, sound_id = parse_source_ids(path.name)
        rows.append({
            "file_path": path.relative_to(extracted_root).as_posix(),
            "species": species,
            "condition": condition,
            "plant_id": record_id if species != "unknown" else "",
            "session_id": "",
            "recording_instance_id": record_id if species == "unknown" else "",
            "sound_id": sound_id,
            "id_source": "supplied Dryad README filename scheme",
        })
    with output.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["file_path", "species", "condition", "plant_id", "session_id", "recording_instance_id", "sound_id", "id_source"])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="Use an already-downloaded official PlantSounds.zip")
    parser.add_argument("--readme", type=Path, help="Preserve the source README that documents filename plant/sound IDs")
    args = parser.parse_args()
    if args.archive and args.archive.stat().st_size > MAX_ARCHIVE_BYTES:
        raise RuntimeError(f"Refusing archive larger than {MAX_ARCHIVE_BYTES} bytes")
    raw = args.archive.read_bytes() if args.archive else download_archive()
    if len(raw) > MAX_ARCHIVE_BYTES or not zipfile.is_zipfile(io.BytesIO(raw)):
        raise RuntimeError("Input is not a valid PlantSounds ZIP archive within the 50 MB limit")
    if DATA_DIR.exists():
        raise FileExistsError(f"Refusing to overwrite existing dataset directory: {DATA_DIR}")
    DATA_DIR.mkdir(parents=True, exist_ok=False)
    readme_hash = None
    if args.readme:
        source_readme = args.readme.resolve()
        if not source_readme.is_file():
            raise FileNotFoundError(source_readme)
        target_readme = DATA_DIR / "README_source.md"
        shutil.copy2(source_readme, target_readme)
        readme_hash = hashlib.sha256(target_readme.read_bytes()).hexdigest()
    archive_copy = DATA_DIR / "PlantSounds.zip"
    archive_copy.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    extracted = DATA_DIR / "raw"
    wav_paths = safe_extract(raw, extracted)
    template = DATA_DIR / "metadata_template.csv"
    rows = write_annotation_template(wav_paths, extracted, template)
    metadata_path = DATA_DIR / "metadata.csv"
    shutil.copy2(template, metadata_path)
    manifest = {
        "source": "Dryad, Recorded plant sounds from: Sounds emitted by plants under stress are airborne and informative",
        "doi": DATASET_DOI,
        "download_url": DOWNLOAD_URL,
        "license_basis": "Dryad states its datasets are published under CC0; cite the dataset as scholarly courtesy.",
        "archive_sha256": digest,
        "archive_bytes": len(raw),
        "wav_files_extracted": len(wav_paths),
        "source_category_rows": rows,
        "metadata_csv": "metadata.csv",
        "sample_details_from_source": "2 ms WAV, 500 kHz",
        "acquired_utc": datetime.now(timezone.utc).isoformat(),
        "plant_id_source": "The supplied Dryad README documents id_<plant_id>_sound_<sound_id>.wav filenames; plant IDs are parsed from the source filename for plant folders. Control IDs are stored as recording_instance_id.",
        "session_ids_provided": False,
        "source_readme_sha256": readme_hash,
        "next_step": "Review the generated metadata template and keep session_id blank unless a source-backed session identifier is available. Plant-grouped evaluation uses plant_id.",
    }
    (DATA_DIR / "source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"dataset_dir": str(DATA_DIR), "wav_files": len(wav_paths), "annotated_category_rows": rows, "template": str(template), "sha256": digest}, indent=2))


if __name__ == "__main__":
    main()
