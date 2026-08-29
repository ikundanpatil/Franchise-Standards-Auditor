from fastapi.testclient import TestClient

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"


def test_register_and_login_flow(client: TestClient) -> None:
    r = client.post(
        REGISTER,
        json={
            "email": "New.User@Demo.io",
            "full_name": "New User",
            "password": "S3curePass!",
            "role": "inspector",
        },
    )
    assert r.status_code == 201, r.text
    assert r.json()["email"] == "new.user@demo.io"  # normalised

    r = client.post(LOGIN, data={"username": "new.user@demo.io", "password": "S3curePass!"})
    assert r.status_code == 200
    tokens = r.json()
    assert tokens["token_type"] == "bearer"
    assert tokens["refresh_token"]

    me = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert me.status_code == 200
    assert me.json()["role"] == "inspector"


def test_cannot_self_register_as_admin(client: TestClient) -> None:
    r = client.post(
        REGISTER,
        json={"email": "x@y.io", "full_name": "X", "password": "S3curePass!", "role": "admin"},
    )
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "permission_denied"


def test_duplicate_email_conflict(client: TestClient) -> None:
    payload = {"email": "dup@demo.io", "full_name": "Dup", "password": "S3curePass!"}
    assert client.post(REGISTER, json=payload).status_code == 201
    r = client.post(REGISTER, json=payload)
    assert r.status_code == 409


def test_wrong_password_rejected(client: TestClient) -> None:
    client.post(REGISTER, json={"email": "a@b.io", "full_name": "A", "password": "S3curePass!"})
    r = client.post(LOGIN, data={"username": "a@b.io", "password": "nope"})
    assert r.status_code == 401


def test_refresh_returns_new_access_token(client: TestClient) -> None:
    client.post(REGISTER, json={"email": "r@b.io", "full_name": "R", "password": "S3curePass!"})
    tokens = client.post(LOGIN, data={"username": "r@b.io", "password": "S3curePass!"}).json()
    r = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200
    assert r.json()["access_token"]


def test_protected_route_requires_token(client: TestClient) -> None:
    assert client.get("/api/v1/auth/me").status_code == 401


def test_admin_can_change_role(client: TestClient, admin_headers: dict) -> None:
    client.post(
        REGISTER, json={"email": "promote@b.io", "full_name": "P", "password": "S3curePass!"}
    )
    users = client.get("/api/v1/auth/users", headers=admin_headers).json()
    target = next(u for u in users if u["email"] == "promote@b.io")

    r = client.patch(
        f"/api/v1/auth/users/{target['id']}/role",
        headers=admin_headers,
        json={"role": "area_manager"},
    )
    assert r.status_code == 200
    assert r.json()["role"] == "area_manager"


def test_non_admin_cannot_list_users(client: TestClient, inspector_headers: dict) -> None:
    assert client.get("/api/v1/auth/users", headers=inspector_headers).status_code == 403


def test_rocketride_bridge_is_not_implemented(client: TestClient) -> None:
    r = client.post("/api/v1/auth/rocketride", json={"assertion": "dummy"})
    assert r.status_code == 501
    assert r.json()["error"]["code"] == "not_implemented"
