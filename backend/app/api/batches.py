from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.api.dependencies import require_roles
from backend.app.domain.auth import UserRole
from backend.app.importing.import_preview import REQUIRED_DATASET_FILES
from backend.app.services.runtime_store import batch_summary, list_batches, read_batch_file, update_batch_file


router = APIRouter(
    prefix="/api/batches",
    tags=["batches"],
    dependencies=[Depends(require_roles(UserRole.TRAINING_OFFICE))],
)


class CsvSaveRequest(BaseModel):
    rows: list[dict[str, str]]


@router.get("")
def get_batches() -> dict[str, object]:
    return {"batches": list_batches()}


@router.get("/{batch_code}")
def get_batch(batch_code: str) -> dict[str, object]:
    return batch_summary(batch_code)


@router.get("/{batch_code}/files")
def get_batch_files(batch_code: str) -> dict[str, object]:
    return {"batch": batch_summary(batch_code), "files": [{"file": name, "row_count": read_batch_file(batch_code, name)["row_count"]} for name in REQUIRED_DATASET_FILES]}


@router.get("/{batch_code}/files/{file_name}")
def get_batch_file(batch_code: str, file_name: str) -> dict[str, object]:
    return read_batch_file(batch_code, file_name)


@router.put("/{batch_code}/files/{file_name}")
def put_batch_file(batch_code: str, file_name: str, request: CsvSaveRequest) -> dict[str, object]:
    return update_batch_file(batch_code, file_name, request.rows)
