from fastapi.testclient import TestClient

STORES = "/api/v1/stores"


def _new_store(client: TestClient, headers: dict, **over) -> dict:
    payload = {
        "code": over.get("code", "#500"),
        "name": over.get("name", "Test Store"),
        "region": over.get("region", "Midtown"),
        "address": "1 Test Way",
        "risk_level": over.get("risk_level", "medium"),
        "compliance_score": over.get("compliance_score", 80),
    }
    r = client.post(STORES, headers=headers, json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def test_manager_can_create_and_list_stores(client: TestClient, manager_headers: dict) -> None:
    _new_store(client, manager_headers, code="#501", name="Alpha")
    _new_store(client, manager_headers, code="#502", name="Beta", risk_level="high")

    page = client.get(STORES, headers=manager_headers).json()
    assert page["total"] == 2
    assert {s["code"] for s in page["items"]} == {"#501", "#502"}


def test_store_list_filters(client: TestClient, manager_headers: dict) -> None:
    _new_store(client, manager_headers, code="#601", name="Coffee One", risk_level="low")
    _new_store(client, manager_headers, code="#602", name="Coffee Two", risk_level="critical")

    high = client.get(STORES, headers=manager_headers, params={"risk_level": "critical"}).json()
    assert [s["code"] for s in high["items"]] == ["#602"]

    search = client.get(STORES, headers=manager_headers, params={"q": "two"}).json()
    assert [s["code"] for s in search["items"]] == ["#602"]


def test_inspector_cannot_create_store(client: TestClient, inspector_headers: dict) -> None:
    r = client.post(
        STORES,
        headers=inspector_headers,
        json={"code": "#700", "name": "X", "region": "Y", "address": "Z"},
    )
    assert r.status_code == 403


def test_duplicate_code_conflict(client: TestClient, manager_headers: dict) -> None:
    _new_store(client, manager_headers, code="#800")
    r = client.post(
        STORES,
        headers=manager_headers,
        json={"code": "#800", "name": "Dup", "region": "M", "address": "A"},
    )
    assert r.status_code == 409


def test_update_and_delete_store(
    client: TestClient, manager_headers: dict, admin_headers: dict
) -> None:
    store = _new_store(client, manager_headers, code="#900")

    upd = client.patch(
        f"{STORES}/{store['id']}", headers=manager_headers, json={"compliance_score": 55}
    )
    assert upd.status_code == 200
    assert upd.json()["compliance_score"] == 55

    # Only admin may delete.
    assert client.delete(f"{STORES}/{store['id']}", headers=manager_headers).status_code == 403
    assert client.delete(f"{STORES}/{store['id']}", headers=admin_headers).status_code == 200
    assert client.get(f"{STORES}/{store['id']}", headers=manager_headers).status_code == 404


def test_store_history_shape(client: TestClient, manager_headers: dict) -> None:
    store = _new_store(client, manager_headers, code="#950")
    hist = client.get(f"{STORES}/{store['id']}/history", headers=manager_headers).json()
    assert hist["store_id"] == store["id"]
    assert hist["inspections_total"] == 0
    assert hist["risk_series"] == []
