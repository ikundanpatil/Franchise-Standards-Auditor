from fastapi.testclient import TestClient

from app.models.enums import RiskLevel
from app.services.ai.engine import AnalysisContext
from app.services.ai.simulated import SimulatedVisionEngine


def test_engine_info_endpoint(client: TestClient, inspector_headers: dict) -> None:
    info = client.get("/api/v1/ai/engine", headers=inspector_headers).json()
    assert info["provider"] == "simulated"
    assert info["ready"] is True
    assert info["catalog_size"] == 10


def test_simulated_engine_is_seed_deterministic() -> None:
    engine = SimulatedVisionEngine()
    ctx = AnalysisContext(
        store_id="s1",
        store_name="Test",
        store_code="#1",
        store_risk=RiskLevel.HIGH,
        store_compliance_score=60,
        seed=99,
    )
    a = engine.analyze(ctx)
    b = engine.analyze(ctx)
    assert [d["type_code"] for d in a.detections] == [d["type_code"] for d in b.detections]
    assert a.risk_score == b.risk_score
    assert a.headline == b.headline


def test_low_risk_store_can_come_back_clean() -> None:
    engine = SimulatedVisionEngine()
    ctx = AnalysisContext(
        store_id="s2",
        store_name="Clean",
        store_code="#2",
        store_risk=RiskLevel.LOW,
        store_compliance_score=97,
        seed=1,
    )
    outcome = engine.analyze(ctx)
    assert outcome.risk_score >= 0
    assert isinstance(outcome.narrative, str) and outcome.narrative


def test_analyze_by_store_id_without_inspection(
    client: TestClient, manager_headers: dict, inspector_headers: dict
) -> None:
    store = client.post(
        "/api/v1/stores",
        headers=manager_headers,
        json={"code": "#ai1", "name": "AdHoc", "region": "X", "address": "Y", "risk_level": "high"},
    ).json()

    r = client.post(
        "/api/v1/ai/analyze",
        headers=inspector_headers,
        json={"store_id": store["id"], "image_label": "walk-in", "seed": 8},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["inspection_id"] is None
    assert body["store_id"] == store["id"]
    assert body["status"] == "completed"

    # It is retrievable from the analyses list.
    listed = client.get(
        "/api/v1/ai/analyses", headers=inspector_headers, params={"store_id": store["id"]}
    ).json()
    assert listed["total"] == 1


def test_analyze_requires_a_target(client: TestClient, inspector_headers: dict) -> None:
    r = client.post("/api/v1/ai/analyze", headers=inspector_headers, json={"seed": 1})
    assert r.status_code == 422
