"""End-to-end inspection flow: upload → analyze → risk → report, dashboard, WS."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.services import risk_service

FAKE_JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01fake-image-bytes-for-tests"


def _store(client: TestClient, headers: dict, code: str = "#FLW1") -> dict:
    return client.post(
        "/api/v1/stores",
        headers=headers,
        json={
            "code": code,
            "name": "Flow Diner",
            "region": "Mumbai",
            "address": "1 Test Rd",
            "risk_level": "medium",
            "compliance_score": 78,
        },
    ).json()


def _upload(client: TestClient, headers: dict, store_id: str, **form) -> dict:
    r = client.post(
        "/api/v1/inspection/upload",
        headers=headers,
        data={"store_id": store_id, **form},
        files=[("images", ("floor.jpg", FAKE_JPEG, "image/jpeg"))],
    )
    assert r.status_code == 200, r.text
    return r.json()


def test_upload_creates_inspection_without_supabase(
    client: TestClient, manager_headers: dict, inspector_headers: dict
) -> None:
    store = _store(client, manager_headers)
    body = _upload(client, inspector_headers, store["id"])

    assert body["status"] == "in_progress"
    assert body["evidence_count"] == 1
    assert body["images"][0]["stored"] is False  # Supabase not configured in tests
    assert any("Supabase" in w for w in body["warnings"])
    assert body["ws_url"].endswith(body["inspection_id"])


def test_full_pipeline_simulated(
    client: TestClient, manager_headers: dict, inspector_headers: dict
) -> None:
    store = _store(client, manager_headers, code="#FLW2")
    up = _upload(
        client,
        inspector_headers,
        store["id"],
        checklist='[{"area":"Staff Hygiene","ok":false}]',
    )

    r = client.post(
        "/api/v1/inspection/analyze",
        headers=inspector_headers,
        json={"inspection_id": up["inspection_id"], "seed": 11},
    )
    assert r.status_code == 200, r.text
    res = r.json()

    assert res["vision_backend"] in ("simulated", "yolo")
    assert res["violations_persisted"] == len(res["detections"])
    assert res["risk"]["risk_score"] >= 0
    assert res["risk"]["compliance_score"] == 100 - res["risk"]["risk_score"]
    assert res["report"] is not None and res["report"]["pending"] is False

    # Violations really are in Postgres.
    vios = client.get(
        f"/api/v1/inspections/{up['inspection_id']}/violations", headers=inspector_headers
    ).json()
    assert len(vios) == res["violations_persisted"]

    # Report is retrievable and final-shaped.
    rep = client.get(f"/api/v1/reports/{res['report']['id']}", headers=inspector_headers).json()
    assert rep["reference"] == res["report"]["reference"]
    assert (
        rep["minor_count"] + rep["major_count"] + rep["critical_count"]
        == res["violations_persisted"]
    )


def test_pipeline_background_report(
    client: TestClient, manager_headers: dict, inspector_headers: dict
) -> None:
    store = _store(client, manager_headers, code="#FLW3")
    up = _upload(client, inspector_headers, store["id"])

    r = client.post(
        "/api/v1/inspection/analyze",
        headers=inspector_headers,
        json={"inspection_id": up["inspection_id"], "seed": 4, "background_report": True},
    )
    assert r.status_code == 200, r.text
    res = r.json()
    assert res["report"]["pending"] is True

    # BackgroundTasks run after the response in TestClient; the report is now final.
    rep = client.get(f"/api/v1/reports/{res['report']['id']}", headers=inspector_headers).json()
    assert rep["status"] in ("final", "draft")
    assert rep["summary"] != "Report generation in progress…"


def test_dashboard_summary_reflects_analysis(
    client: TestClient, manager_headers: dict, inspector_headers: dict
) -> None:
    before = client.get("/api/v1/dashboard/summary", headers=manager_headers).json()
    assert before["kpis"]["total_stores"] == 0

    store = _store(client, manager_headers, code="#FLW4")
    up = _upload(client, inspector_headers, store["id"])
    client.post(
        "/api/v1/inspection/analyze",
        headers=inspector_headers,
        json={"inspection_id": up["inspection_id"], "seed": 7},
    )

    after = client.get("/api/v1/dashboard/summary", headers=manager_headers).json()
    assert after["kpis"]["total_stores"] == 1
    assert after["kpis"]["completed_last_30d"] >= 1
    assert sum(after["risk_distribution"].values()) == 1
    assert "compliance_trend" in after and len(after["compliance_trend"]) == 6


def test_risk_history_endpoint(
    client: TestClient, manager_headers: dict, inspector_headers: dict
) -> None:
    store = _store(client, manager_headers, code="#FLW5")
    up = _upload(client, inspector_headers, store["id"])
    client.post(
        "/api/v1/inspection/analyze",
        headers=inspector_headers,
        json={"inspection_id": up["inspection_id"], "seed": 2},
    )

    hist = client.get(f"/api/v1/stores/{store['id']}/risk-history", headers=manager_headers).json()
    assert hist["store_id"] == store["id"]
    assert hist["window_days"] == 90
    assert len(hist["points"]) == 1
    p = hist["points"][0]
    assert p["risk_score"] >= 0 and p["compliance_score"] == 100 - p["risk_score"]


def test_ws_streams_progress(
    client: TestClient, manager_headers: dict, inspector_headers: dict
) -> None:
    store = _store(client, manager_headers, code="#FLW6")
    up = _upload(client, inspector_headers, store["id"])
    token = inspector_headers["Authorization"].split(" ", 1)[1]

    with client.websocket_connect(
        f"/api/v1/ws/inspections/{up['inspection_id']}?token={token}"
    ) as ws:
        hello = ws.receive_json()
        assert hello["stage"] == "connected"

        client.post(
            "/api/v1/inspection/analyze",
            headers=inspector_headers,
            json={"inspection_id": up["inspection_id"], "seed": 9},
        )

        stages: list[str] = []
        for _ in range(12):
            evt = ws.receive_json()
            stages.append(evt["stage"])
            if evt["stage"] in ("done", "error"):
                break
        assert "done" in stages
        assert any(s in stages for s in ("detecting", "scoring", "report"))


def test_ws_rejects_missing_token(client: TestClient) -> None:
    from starlette.websockets import WebSocketDisconnect

    try:
        with client.websocket_connect("/api/v1/ws/inspections/" + "0" * 8):
            raise AssertionError("should have been rejected")
    except WebSocketDisconnect as exc:
        assert exc.code == 1008


def test_risk_engine_math() -> None:
    a = risk_service.assess(
        violations=[
            {"severity": "critical"},
            {"severity": "major"},
            {"severity": "minor", "status": "resolved"},  # ignored
        ],
        checklist=[{"area": "x", "ok": False}, {"area": "y", "ok": True}],
        complaint_severity="major",
    )
    # 34 + 16 + (1 failed * 4) + 8 complaint = 62
    assert a.risk_score == 62
    assert a.compliance_score == 38
    assert a.risk_level.value == "critical"
    assert a.counts == {"minor": 0, "major": 1, "critical": 1}
    assert a.breakdown == {"violations": 50, "checklist": 4, "complaint": 8}
