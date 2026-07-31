from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from backend.app.importing.csv_validator import CsvValidationError, validate_sample_dataset


REQUIRED_DATASET_FILES = (
    "lecturers.csv",
    "rooms.csv",
    "time_slots.csv",
    "course_sections.csv",
    "lecturer_time_preferences.csv",
    "room_unavailable_slots.csv",
    "academic_calendar.csv",
)


@dataclass(frozen=True)
class CsvFilePreview:
    file: str
    headers: tuple[str, ...]
    sample_rows: tuple[dict[str, str], ...]
    row_count: int


@dataclass(frozen=True)
class DatasetPreviewResult:
    files: tuple[CsvFilePreview, ...]
    errors: tuple[CsvValidationError, ...]

    @property
    def is_valid(self) -> bool:
        return not self.errors


def preview_and_validate_dataset(directory: str | Path, sample_size: int = 5) -> DatasetPreviewResult:
    base_dir = Path(directory)
    previews = tuple(_preview_csv_file(base_dir / file_name, file_name, sample_size) for file_name in REQUIRED_DATASET_FILES)
    validation_result = validate_sample_dataset(base_dir)
    return DatasetPreviewResult(files=previews, errors=validation_result.errors)


def _preview_csv_file(path: Path, file_name: str, sample_size: int) -> CsvFilePreview:
    if not path.exists():
        return CsvFilePreview(file=file_name, headers=(), sample_rows=(), row_count=0)

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            headers = tuple(reader.fieldnames or ())
            rows: list[dict[str, str]] = []
            row_count = 0
            for row_count, row in enumerate(reader, start=1):
                if len(rows) < sample_size:
                    rows.append({key: (value or "").strip() for key, value in row.items()})
    except (UnicodeDecodeError, csv.Error):
        return CsvFilePreview(file=file_name, headers=(), sample_rows=(), row_count=0)
    return CsvFilePreview(
        file=file_name,
        headers=headers,
        sample_rows=tuple(rows),
        row_count=row_count,
    )
