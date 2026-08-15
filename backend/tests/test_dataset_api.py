from __future__ import annotations

import shutil

from backend.app.api import datasets
from backend.tests.auth_helpers import authenticated_client


def test_official_dataset_file_list_and_read_endpoint() -> None:
    client = authenticated_client()

    list_response = client.get("/api/datasets/official/files")
    assert list_response.status_code == 200
    payload = list_response.json()
    assert any(file["file"] == "lecturers.csv" for file in payload["files"])

    read_response = client.get("/api/datasets/official/files/lecturers.csv")
    assert read_response.status_code == 200
    file_payload = read_response.json()
    assert "lecturer_code" in file_payload["headers"]
    assert "lecturer_name" in file_payload["headers"]
    assert file_payload["row_count"] >= 20


def test_rejects_invalid_dataset_change_without_overwriting_file(tmp_path, monkeypatch) -> None:
    official_copy = tmp_path / "official"
    shutil.copytree(datasets.OFFICIAL_DATASET_DIR, official_copy)
    monkeypatch.setattr(datasets, "OFFICIAL_DATASET_DIR", official_copy)
    client = authenticated_client()

    original_content = (official_copy / "rooms.csv").read_text(encoding="utf-8")
    response = client.put("/api/datasets/official/files/rooms.csv", json={"rows": []})

    assert response.status_code == 422
    assert response.json()["detail"]["errors"]
    assert (official_copy / "rooms.csv").read_text(encoding="utf-8") == original_content


def test_saved_dataset_file_uses_utf8_bom_for_excel(tmp_path, monkeypatch) -> None:
    official_copy = tmp_path / "official"
    shutil.copytree(datasets.OFFICIAL_DATASET_DIR, official_copy)
    monkeypatch.setattr(datasets, "OFFICIAL_DATASET_DIR", official_copy)
    client = authenticated_client()

    original_rows = client.get("/api/datasets/official/files/rooms.csv").json()["rows"]
    response = client.put("/api/datasets/official/files/rooms.csv", json={"rows": original_rows})

    assert response.status_code == 200
    assert (official_copy / "rooms.csv").read_bytes().startswith(b"\xef\xbb\xbf")
