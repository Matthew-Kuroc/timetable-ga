from __future__ import annotations

import shutil
from pathlib import Path

from backend.app.services import runtime_store


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_editing_confirmed_batch_creates_new_version(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(runtime_store, "RUNTIME_ROOT", tmp_path / "runtime")
    monkeypatch.setattr(runtime_store, "BATCH_ROOT", tmp_path / "runtime" / "batches")
    source = tmp_path / "source"
    shutil.copytree(REPO_ROOT / "data" / "samples" / "small", source)

    original = runtime_store.create_confirmed_batch(source)
    original_rows = runtime_store.read_batch_file(str(original["batch_code"]), "lecturers.csv")["rows"]
    changed_rows = [dict(row) for row in original_rows]
    changed_rows[0]["lecturer_name"] = "Tên phiên bản mới"

    saved = runtime_store.update_batch_file(str(original["batch_code"]), "lecturers.csv", changed_rows)
    updated_code = str(saved["batch"]["batch_code"])

    assert updated_code != original["batch_code"]
    assert runtime_store.read_batch_file(str(original["batch_code"]), "lecturers.csv")["rows"][0]["lecturer_name"] != "Tên phiên bản mới"
    assert runtime_store.read_batch_file(updated_code, "lecturers.csv")["rows"][0]["lecturer_name"] == "Tên phiên bản mới"


def test_confirmed_batch_keeps_display_metadata_and_confirmation_time(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(runtime_store, "RUNTIME_ROOT", tmp_path / "runtime")
    monkeypatch.setattr(runtime_store, "BATCH_ROOT", tmp_path / "runtime" / "batches")
    source = tmp_path / "source"
    shutil.copytree(REPO_ROOT / "data" / "samples" / "small", source)

    batch = runtime_store.create_confirmed_batch(
        source,
        display_name="TKB Học kỳ 1 — Đợt đăng ký 1",
        semester="Học kỳ 1",
        academic_year="2026–2027",
        note="Dữ liệu kiểm tra",
    )

    assert batch["display_name"] == "TKB Học kỳ 1 — Đợt đăng ký 1"
    assert batch["semester"] == "Học kỳ 1"
    assert batch["academic_year"] == "2026–2027"
    assert batch["version_number"] == 1
    assert "T" in str(batch["confirmed_at"])


def test_list_runs_returns_newest_compact_summaries(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(runtime_store, "RUN_ROOT", tmp_path / "runtime" / "runs")
    first = {
        "batch_code": "BATCH-OLD",
        "status": "COMPLETED",
        "generation_count": 20,
        "seed": 42,
        "evaluation": {"hard_violation_count": 0, "soft_cost": 15.0},
        "assignments": [{"section_code": "IT101_01"}],
    }
    second = {
        "batch_code": "BATCH-NEW",
        "status": "COMPLETED",
        "generation_count": 30,
        "seed": 43,
        "evaluation": {"hard_violation_count": 0, "soft_cost": 12.0},
        "assignments": [{"section_code": "IT101_01"}, {"section_code": "IT101_02"}],
    }

    first_code = runtime_store.create_run(first)
    second_code = runtime_store.create_run(second)
    first["run_code"], first["created_at"] = first_code, "2026-01-01T00:00:00+00:00"
    second["run_code"], second["created_at"] = second_code, "2026-01-01T00:00:01+00:00"
    runtime_store.write_run(first_code, first)
    runtime_store.write_run(second_code, second)

    summaries = runtime_store.list_runs()

    assert [item["run_code"] for item in summaries] == [second_code, first_code]
    assert summaries[0]["assignment_count"] == 2
    assert "assignments" not in summaries[0]
