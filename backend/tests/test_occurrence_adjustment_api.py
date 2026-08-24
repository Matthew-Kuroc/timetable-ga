from __future__ import annotations

import shutil
import zipfile
from datetime import date
from io import BytesIO
from pathlib import Path

import pytest
from sqlalchemy import select


fastapi = pytest.importorskip("fastapi")
pytest.importorskip("pydantic")

from backend.app.services import runtime_store
from backend.app.db.models import ScheduleChangeLogModel
from backend.app.db.session import get_session_local
from backend.tests.auth_helpers import authenticated_client


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_direct_adjustment_changes_only_one_dated_occurrence_on_official_timetable(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(runtime_store, "BATCH_ROOT", tmp_path / "runtime" / "batches")
    monkeypatch.setattr(runtime_store, "RUN_ROOT", tmp_path / "runtime" / "runs")
    source = tmp_path / "source"
    shutil.copytree(REPO_ROOT / "data" / "samples" / "small", source)
    batch = runtime_store.create_confirmed_batch(source)
    client = authenticated_client()

    run_response = client.post("/api/ga/runs/preview", json={"batch_code": batch["batch_code"], "population_size": 12, "generations": 4, "seed": 42})
    assert run_response.status_code == 200
    run = run_response.json()
    publish_response = client.post(f"/api/ga/runs/{run['run_code']}/publish", json={"note": "Công bố để kiểm thử"})
    assert publish_response.status_code == 200
    official = publish_response.json()
    occurrence = run["occurrences"][0]
    response = client.put(
        f"/api/ga/official-timetables/{official['official_code']}/adjustments",
        json={
            "section_code": occurrence["section_code"],
            "scope": "ONE_OCCURRENCE",
            "occurrence_date": occurrence["date"],
            "room_code": occurrence["room_code"],
            "slot_code": occurrence["slot_code"],
            "reason": "Kiểm tra điều chỉnh một buổi học",
        },
    )

    assert response.status_code == 200
    updated = response.json()["official"]
    assert updated["assignments"] == run["assignments"]
    changed = next(item for item in updated["occurrences"] if item["section_code"] == occurrence["section_code"] and item["date"] == occurrence["date"])
    assert changed["status"] == "EXCEPTION"
    assert updated["change_history"][-1]["scope"] == "ONE_OCCURRENCE"
    assert updated["change_history"][-1]["changed_by"] == "training_office"
    with get_session_local()() as session:
        change_log = session.scalar(select(ScheduleChangeLogModel))
        assert change_log is not None
        assert change_log.changed_by == "training_office"
    assert updated["change_history"][-1]["reason"] == "Kiểm tra điều chỉnh một buổi học"

    original_run_response = client.get(f"/api/ga/runs/{run['run_code']}")
    assert original_run_response.json()["occurrences"] == run["occurrences"]
    export_response = client.get(f"/api/ga/official-timetables/{official['official_code']}/export.csv")
    assert export_response.status_code == 200
    assert "date,academic_week,status,section_code" in export_response.text
    assert date.fromisoformat(occurrence["date"]).strftime("%d-%m-%Y") in export_response.text
    xlsx_response = client.get(f"/api/ga/official-timetables/{official['official_code']}/export.xlsx")
    assert xlsx_response.status_code == 200
    assert xlsx_response.headers["content-type"].startswith("application/vnd.openxmlformats")
    disposition = xlsx_response.headers["content-disposition"]
    assert disposition.startswith('attachment; filename="')
    assert f'-{official["official_code"]}-' in disposition
    assert disposition.endswith('.xlsx"')
    with zipfile.ZipFile(BytesIO(xlsx_response.content)) as workbook:
        assert "xl/worksheets/sheet1.xml" in workbook.namelist()
        assert occurrence["section_code"] in workbook.read("xl/worksheets/sheet1.xml").decode("utf-8")
