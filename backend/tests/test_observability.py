from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_correlation_id() -> None:
    with TestClient(app) as client:
        response = client.get("/health", headers={"X-Correlation-ID": "test-correlation-id"})

    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == "test-correlation-id"
    assert response.json() == {"status": "ok"}


def test_readiness_checks_database() -> None:
    with TestClient(app) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "ok"}
    assert response.headers.get("X-Correlation-ID")
