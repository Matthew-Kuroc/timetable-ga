from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from backend.app.api.dependencies import require_roles
from backend.app.domain.auth import UserRole
from backend.app.importing.import_preview import (
    REQUIRED_DATASET_FILES,
    DatasetPreviewResult,
    preview_and_validate_dataset,
)
from backend.app.services.runtime_store import create_confirmed_batch


router = APIRouter(
    prefix="/api/imports",
    tags=["imports"],
    dependencies=[Depends(require_roles(UserRole.TRAINING_OFFICE))],
)


@router.post("/csv/preview")
async def preview_csv_dataset(files: list[UploadFile] = File(...)) -> dict[str, object]:
    received = {file.filename or "": file for file in files}
    missing = [file_name for file_name in REQUIRED_DATASET_FILES if file_name not in received]
    unexpected = [file_name for file_name in received if file_name not in REQUIRED_DATASET_FILES]
    if missing:
        raise HTTPException(status_code=400, detail={"message": "Thiếu file CSV bắt buộc.", "missing_files": missing})
    if unexpected:
        raise HTTPException(status_code=400, detail={"message": "File CSV không nằm trong schema MVP.", "unexpected_files": unexpected})

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        for file_name in REQUIRED_DATASET_FILES:
            destination = temp_path / file_name
            with destination.open("wb") as output:
                shutil.copyfileobj(received[file_name].file, output)

        result = preview_and_validate_dataset(temp_path)
    return _preview_result_to_response(result)


@router.post("/csv/confirm")
async def confirm_csv_dataset(
    files: list[UploadFile] = File(...),
    display_name: str = Form("", max_length=120),
    semester: str = Form("", max_length=50),
    academic_year: str = Form("", max_length=30),
    note: str = "",
) -> dict[str, object]:
    received = {file.filename or "": file for file in files}
    missing = [file_name for file_name in REQUIRED_DATASET_FILES if file_name not in received]
    unexpected = [file_name for file_name in received if file_name not in REQUIRED_DATASET_FILES]
    if missing or unexpected:
        raise HTTPException(status_code=400, detail={"message": "Bộ CSV phải gồm đúng 7 file theo mẫu.", "missing_files": missing, "unexpected_files": unexpected})
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        for file_name in REQUIRED_DATASET_FILES:
            with (temp_path / file_name).open("wb") as output:
                shutil.copyfileobj(received[file_name].file, output)
        return {"batch": create_confirmed_batch(temp_path, display_name=display_name, semester=semester, academic_year=academic_year, note=note), "message": "Đã xác nhận bộ dữ liệu. Bạn có thể chỉnh sửa hoặc chạy GA với bộ này."}


def _preview_result_to_response(result: DatasetPreviewResult) -> dict[str, object]:
    return {
        "valid": result.is_valid,
        "files": [
            {
                "file": file_preview.file,
                "headers": list(file_preview.headers),
                "sample_rows": list(file_preview.sample_rows),
                "row_count": file_preview.row_count,
            }
            for file_preview in result.files
        ],
        "errors": [
            {
                "file": error.file,
                "row": error.row,
                "column": error.column,
                "value": error.value,
                "reason": error.reason,
            }
            for error in result.errors
        ],
    }
