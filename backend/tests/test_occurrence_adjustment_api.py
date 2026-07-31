from __future__ import annotations

import shutil
from pathlib import Path

import pytest


fastapi = pytest.importorskip("fastapi")
pytest.importorskip("pydantic")

from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.services import runtime_store


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_direct_adjustment_changes_only_one_dated_occurrence(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(runtime_store, "BATCH_ROOT", tmp_path / "runtime" / "batches")
    monkeypatch.setattr(runtime_store, "RUN_ROOT", tmp_path / "runtime" / "runs")
    source = tmp_path / "source"
    shutil.copytree(REPO_ROOT / "data" / "samples" / "small", source)
    batch = runtime_store.create_confirmed_batch(source)
    client = TestClient(create_app())

    run_response = client.post("/api/ga/runs/preview", json={"batch_code": batch["batch_code"], "population_size": 12, "generations": 4, "seed": 42})
    assert run_response.status_code == 200
    run = run_response.json()
    occurrence = run["occurrences"][0]
    response = client.put(
        f"/api/ga/runs/{run['run_code']}/occurrences",
        json={
            "section_code": occurrence["section_code"],
            "occurrence_date": occurrence["date"],
            "new_date": occurrence["date"],
            "room_code": occurrence["room_code"],
            "slot_code": occurrence["slot_code"],
            "reason": "Kiểm tra điều chỉnh một buổi học",
        },
    )

    assert response.status_code == 200
    updated = response.json()["run"]
    assert updated["assignments"] == run["assignments"]
    changed = next(item for item in updated["occurrences"] if item["section_code"] == occurrence["section_code"] and item["date"] == occurrence["date"])
    assert changed["status"] == "EXCEPTION"
    assert updated["change_history"][-1]["scope"] == "ONE_OCCURRENCE"
    assert updated["change_history"][-1]["reason"] == "Kiểm tra điều chỉnh một buổi học"

    export_response = client.get(f"/api/ga/runs/{run['run_code']}/export.csv")
    assert export_response.status_code == 200
    assert "date,academic_week,status,section_code" in export_response.text
    assert occurrence["date"] in export_response.text
