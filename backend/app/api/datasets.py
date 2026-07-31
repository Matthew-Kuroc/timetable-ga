from __future__ import annotations

import csv
import shutil
import tempfile
from dataclasses import asdict
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.importing.import_preview import REQUIRED_DATASET_FILES
from backend.app.importing.csv_validator import validate_sample_dataset


router = APIRouter(prefix="/api/datasets", tags=["datasets"])

REPO_ROOT = Path(__file__).resolve().parents[3]
OFFICIAL_DATASET_DIR = REPO_ROOT / "data" / "samples" / "official"


class CsvSaveRequest(BaseModel):
    rows: list[dict[str, str]]


@router.get("/official/files")
def list_official_files() -> dict[str, object]:
    return {
        "dataset_dir": str(OFFICIAL_DATASET_DIR),
        "files": [
            _read_csv_file_summary(file_name)
            for file_name in REQUIRED_DATASET_FILES
        ],
    }


@router.get("/official/files/{file_name}")
def read_official_file(file_name: str) -> dict[str, object]:
    path = _resolve_official_csv_path(file_name)
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = [
            {key: value or "" for key, value in row.items()}
            for row in reader
        ]
    return {
        "file": file_name,
        "headers": list(reader.fieldnames or []),
        "rows": rows,
        "row_count": len(rows),
    }


@router.put("/official/files/{file_name}")
def save_official_file(file_name: str, request: CsvSaveRequest) -> dict[str, object]:
    path = _resolve_official_csv_path(file_name)
    existing_headers = _read_headers(path)
    normalized_rows = [
        {header: str(row.get(header, "")) for header in existing_headers}
        for row in request.rows
    ]
    _validate_dataset_change(file_name, existing_headers, normalized_rows)
    _write_csv(path, existing_headers, normalized_rows)
    return {
        "file": file_name,
        "headers": existing_headers,
        "row_count": len(normalized_rows),
        "message": "Đã lưu file CSV mẫu.",
    }


def _read_csv_file_summary(file_name: str) -> dict[str, object]:
    path = _resolve_official_csv_path(file_name)
    headers = _read_headers(path)
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        row_count = max(0, sum(1 for _line in file) - 1)
    return {
        "file": file_name,
        "headers": headers,
        "row_count": row_count,
    }


def _resolve_official_csv_path(file_name: str) -> Path:
    if file_name not in REQUIRED_DATASET_FILES:
        raise HTTPException(status_code=404, detail="File CSV không thuộc bộ official.")
    path = OFFICIAL_DATASET_DIR / file_name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy file CSV.")
    return path


def _read_headers(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader.fieldnames or [])


def _validate_dataset_change(
    file_name: str,
    headers: list[str],
    rows: list[dict[str, str]],
) -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        staged_directory = Path(temporary_directory) / "official"
        shutil.copytree(OFFICIAL_DATASET_DIR, staged_directory)
        _write_csv(staged_directory / file_name, headers, rows)
        validation_result = validate_sample_dataset(staged_directory)
    if validation_result.is_valid:
        return
    raise HTTPException(
        status_code=422,
        detail={
            "message": "Không thể lưu vì bộ dữ liệu CSV có lỗi liên kết hoặc giá trị không hợp lệ.",
            "errors": [asdict(error) for error in validation_result.errors],
        },
    )


def _write_csv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
