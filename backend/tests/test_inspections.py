from fastapi.testclient import TestClient


def _store(client: TestClient, headers: dict, code: str = "#100") -> dict:
    return client.post(
        "/api/v1/stores",
        headers=headers,
        json={
            "code": code,
            "name": "Line Diner",
            "region": "Riverside",
            "address": "1 Dock St",
            "risk_level": "high",
            "compliance_score": 62,
        },
    ).json()


def test_full_inspection_to_report_flow(
    client: TestClient, manager_headers: dict, inspector_headers: dict
) -> None:
    store = _store(client, manager_headers)

    r = client.post(
        "/api/v1/inspections",
        headers=inspector_headers,
        json={
            "store_id": store["id"],
            "method": "ai_photo",
            "checklist": [{"area": "Staff Hygiene", "ok": False, "note": "gloves"}],
            "image_label": "Prep line",
        },
    )
    assert r.status_code == 201, r.text
    inspection = r.json()
    assert inspection["status"] == "scheduled"

    # Analyse — deterministic with a fixed seed.
    a = client.post(
        f"/api/v1/inspections/{inspection['id']}/analyze",
        headers=inspector_headers,
        params={"seed": 3},
    )
    assert a.status_code == 200, a.text
    analysis = a.json()
    assert analysis["status"] == "completed"
    assert analysis["risk_score"] is not None
    assert len(analysis["detections"]) >= 1

    # Detections were written back as violations.
    vios = client.get(
        f"/api/v1/inspections/{inspection['id']}/violations", headers=inspector_headers
    ).json()
    assert len(vios) == len(analysis["detections"])
    assert all(v["confidence"] is not None for v in vios)

    # Report generation.
    rep = client.post(
        "/api/v1/reports",
        headers=inspector_headers,
        json={"inspection_id": inspection["id"], "finalize": True},
    )
    assert rep.status_code == 200, rep.text
    report = rep.json()
    assert report["reference"].startswith("FG-REP-")
    assert report["status"] == "final"
    assert report["minor_count"] + report["major_count"] + report["critical_count"] == len(
        analysis["detections"]
    )

    # PDF download.
    pdf = client.get(f"/api/v1/reports/{report['id']}/pdf", headers=inspector_headers)
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content[:4] == b"%PDF"


def test_analyze_is_deterministic_with_seed(
    client: TestClient, manager_headers: dict, inspector_headers: dict
) -> None:
    # Fresh store each run so prior-run risk recomputation doesn't change the input.
    def run(code: str) -> list[str]:
        store = _store(client, manager_headers, code=code)
        insp = client.post(
            "/api/v1/inspections",
            headers=inspector_headers,
            json={"store_id": store["id"], "method": "ai_photo"},
        ).json()
        res = client.post(
            f"/api/v1/inspections/{insp['id']}/analyze",
            headers=inspector_headers,
            params={"seed": 42},
        ).json()
        return [d["type_code"] for d in res["detections"]]

    assert run("#101a") == run("#101b")


def test_violation_resolution_updates_store_counts(
    client: TestClient, manager_headers: dict, inspector_headers: dict
) -> None:
    store = _store(client, manager_headers, code="#102")
    insp = client.post(
        "/api/v1/inspections",
        headers=inspector_headers,
        json={"store_id": store["id"], "method": "ai_photo"},
    ).json()
    client.post(
        f"/api/v1/inspections/{insp['id']}/analyze",
        headers=inspector_headers,
        params={"seed": 5},
    )
    vios = client.get(
        f"/api/v1/inspections/{insp['id']}/violations", headers=inspector_headers
    ).json()
    assert vios

    r = client.patch(
        f"/api/v1/violations/{vios[0]['id']}",
        headers=manager_headers,
        json={"status": "resolved", "resolution_note": "done"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "resolved"
    assert r.json()["resolved_at"] is not None

    fresh = client.get(f"/api/v1/stores/{store['id']}", headers=manager_headers).json()
    assert fresh["open_violation_count"] == len(vios) - 1


def test_report_requires_analysis_first(
    client: TestClient, manager_headers: dict, inspector_headers: dict
) -> None:
    store = _store(client, manager_headers, code="#103")
    insp = client.post(
        "/api/v1/inspections",
        headers=inspector_headers,
        json={"store_id": store["id"], "method": "ai_photo"},
    ).json()
    r = client.post(
        "/api/v1/reports", headers=inspector_headers, json={"inspection_id": insp["id"]}
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"
