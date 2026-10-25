"""Dependency-light checks for split path and optional group leakage."""

from collections import Counter
from itertools import combinations


def find_overlaps(values_by_split):
    """Return pairwise overlaps for split-name to iterable mappings."""
    normalized = {name: set(values) for name, values in values_by_split.items()}
    return {
        (left_name, right_name): normalized[left_name] & normalized[right_name]
        for left_name, right_name in combinations(normalized, 2)
    }


def assert_no_path_overlap(paths_by_split):
    duplicate_paths = {
        name: {path for path, count in Counter(paths).items() if count > 1}
        for name, paths in paths_by_split.items()
    }
    duplicate_paths = {name: paths for name, paths in duplicate_paths.items() if paths}
    if duplicate_paths:
        details = "; ".join(
            f"{name}: {len(paths)} duplicated path(s) within split"
            for name, paths in duplicate_paths.items()
        )
        raise ValueError(f"Duplicate dataset paths detected: {details}")

    overlaps = find_overlaps(paths_by_split)
    conflicts = {pair: values for pair, values in overlaps.items() if values}
    if conflicts:
        details = "; ".join(
            f"{left}/{right}: {len(paths)} shared path(s)"
            for (left, right), paths in conflicts.items()
        )
        raise ValueError(f"Dataset split path overlap detected: {details}")


def assert_no_group_overlap(groups_by_split):
    overlaps = find_overlaps(groups_by_split)
    conflicts = {pair: values for pair, values in overlaps.items() if values}
    if conflicts:
        details = "; ".join(
            f"{left}/{right}: {len(groups)} shared group(s)"
            for (left, right), groups in conflicts.items()
        )
        raise ValueError(f"Dataset split group overlap detected: {details}")
