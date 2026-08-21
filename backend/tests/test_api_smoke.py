from __future__ import annotations

import pytest


fastapi = pytest.importorskip("fastapi")
pytest.importorskip("pydantic")

from fastapi.testclient import TestClient

from backend.app.domain.auth import UserRole
from backend.app.main import create_app
from backend.tests.auth_helpers import authenticated_client


def test_ga_runtime_requires_confirmed_batch_and_rejects_data_directory() -> None:
    client = authenticated_client(UserRole.TRAINING_OFFICE, username="office_ga_contract")
    response = client.post("/api/ga/runs/preview", json={"data_dir": "data/samples/small"})
    assert response.status_code == 422


def test_health_endpoint() -> None:
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
