
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

import main


@pytest.fixture
def client(monkeypatch):
    # Prevent real Redis connections during tests.
    fake_redis = MagicMock()
    fake_redis.get.return_value = "0"

    monkeypatch.setattr(main, "get_redis", lambda: fake_redis)

    with TestClient(main.app) as test_client:
        yield test_client


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "application": "DevOps Task API",
        "version": "1.0.0",
    }


def test_create_task_validation(client):
    response = client.post("/tasks", json={"title": ""})

    assert response.status_code == 422


def test_create_task_missing_title(client):
    response = client.post("/tasks", json={})

    assert response.status_code == 422


def test_metrics(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.json() == {"total_requests": 0}


def test_health_database_failure(client, monkeypatch):
    import psycopg

    def failed_connection():
        raise psycopg.OperationalError("Database unavailable")

    monkeypatch.setattr(main, "get_connection", failed_connection)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Database unavailable"
    }
