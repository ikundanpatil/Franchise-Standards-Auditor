from fastapi.testclient import TestClient


def test_health_ok(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["ai_provider"] == "simulated"


def test_root_redirects_to_docs(client: TestClient) -> None:
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (307, 308)
    assert resp.headers["location"] == "/docs"


def test_openapi_served(client: TestClient) -> None:
    resp = client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    assert "/api/v1/auth/login" in resp.json()["paths"]


def test_request_id_header_present(client: TestClient) -> None:
    resp = client.get("/api/v1/openapi.json")
    assert resp.headers.get("X-Request-ID")
