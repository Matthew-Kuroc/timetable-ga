from __future__ import annotations

from pathlib import Path

from backend.app.domain.auth import UserRole
from backend.app.importing.import_preview import REQUIRED_DATASET_FILES
from backend.app.services import runtime_store
from backend.tests.auth_helpers import authenticated_client


REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = REPO_ROOT / "data" / "samples" / "small"


def _multipart_files() -> list[tuple[str, tuple[str, bytes, str]]]:
    return [
        ("files", (name, (SAMPLE_DIR / name).read_bytes(), "text/csv"))
        for name in REQUIRED_DATASET_FILES
    ]


def test_upload_confirm_run_publish_and_export_workflow(tmp_path, monkeypatch) -> None:
    runtime_root = tmp_path / "runtime"
    monkeypatch.setattr(runtime_store, "RUNTIME_ROOT", runtime_root)
    monkeypatch.setattr(runtime_store, "BATCH_ROOT", runtime_root / "batches")
    monkeypatch.setattr(runtime_store, "RUN_ROOT", runtime_root / "runs")
    client = authenticated_client(UserRole.TRAINING_OFFICE, username="office_full_workflow")

    preview = client.post("/api/imports/csv/preview", files=_multipart_files())
    assert preview.status_code == 200
    assert preview.json()["valid"] is True
    assert len(preview.json()["files"]) == 7

    confirm = client.post(
        "/api/imports/csv/confirm",
        files=_multipart_files(),
        data={"display_name": "Kiểm thử luồng đầy đủ", "semester": "HK1", "academic_year": "2026-2027"},
    )
    assert confirm.status_code == 200
    batch_code = confirm.json()["batch"]["batch_code"]

    run_response = client.post(
        "/api/ga/runs/preview",
        json={"batch_code": batch_code, "population_size": 12, "generations": 4, "seed": 42},
    )
    assert run_response.status_code == 200
    run = run_response.json()
    assert run["batch_code"] == batch_code
    assert run["evaluation"]["hard_violation_count"] == 0

    publish = client.post(f"/api/ga/runs/{run['run_code']}/publish", json={"note": "Kiểm thử luồng đầy đủ"})
    assert publish.status_code == 200
    official = publish.json()
    assert official["source_run_code"] == run["run_code"]

    export = client.get(f"/api/ga/official-timetables/{official['official_code']}/export.csv")
    assert export.status_code == 200
    assert "Kiem thu luong day du" in export.headers["content-disposition"]
    assert any(item["section_code"] in export.text for item in run["assignments"])
