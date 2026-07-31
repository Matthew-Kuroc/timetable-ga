from __future__ import annotations

import pytest


fastapi = pytest.importorskip("fastapi")
pytest.importorskip("pydantic")

from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
