import pytest
import json
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.schemas import LeadAnalysis, RelevantProductItem

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "products_count" in data
    assert data["products_count"] >= 10

def test_list_products():
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 10
    product_names = [p["name"] for p in data]
    assert "CRM Automation Suite" in product_names
    assert "AI Customer Support Platform" in product_names

def test_analyze_empty_requirement_validation():
    response = client.post("/api/leads/analyze", json={"requirement": "   "})
    assert response.status_code == 422

def test_analyze_short_requirement_validation():
    response = client.post("/api/leads/analyze", json={"requirement": "hi"})
    assert response.status_code == 422

def test_analyze_missing_api_key():
    # Ensure without API key it returns 503 with helpful detail
    with patch("backend.ai.groq_client.settings.GROQ_API_KEY", ""):
        with patch.dict("os.environ", {"GROQ_API_KEY": ""}):
            response = client.post(
                "/api/leads/analyze",
                json={"requirement": "We need an AI customer support platform with automated responses"}
            )
            assert response.status_code == 503
            assert "GROQ_API_KEY is not configured" in response.json()["detail"]

def test_analyze_lead_with_mocked_groq():
    mock_analysis = LeadAnalysis(
        lead_summary="Growing e-commerce company looking for automated support resolution.",
        relevant_products=[
            RelevantProductItem(
                name="AI Customer Support Platform",
                reason="Provides 24/7 automated resolution for tier-1 customer inquiries."
            )
        ],
        potential_customer_needs=[
            "Automate repetitive support tickets",
            "Multi-channel support integration"
        ],
        recommended_next_step="Schedule a live product demonstration of AI customer support workflows.",
        follow_up_questions=[
            "What is your average monthly ticket volume?",
            "Which helpdesk software are you currently using?"
        ],
        lead_score=88,
        priority="High"
    )

    with patch("backend.main.analyze_lead_with_groq", return_value=mock_analysis):
        req_text = "We are an online retailer needing automated ticket deflection and chat bots."
        response = client.post(
            "/api/leads/analyze",
            json={"requirement": req_text}
        )
        assert response.status_code == 201
        data = response.json()
        assert "lead_id" in data
        assert data["requirement"] == req_text
        assert len(data["retrieved_products"]) == 3
        assert data["analysis"]["lead_summary"] == mock_analysis.lead_summary
        assert data["analysis"]["lead_score"] == 88
        assert data["analysis"]["priority"] == "High"

        # Verify it is also stored and retrievable via GET /api/leads
        history_resp = client.get("/api/leads")
        assert history_resp.status_code == 200
        history_data = history_resp.json()
        assert len(history_data) >= 1
        assert history_data[0]["id"] == data["lead_id"]
        assert history_data[0]["customer_requirement"] == req_text
