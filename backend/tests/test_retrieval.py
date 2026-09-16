import pytest
from backend.retrieval.retriever import retrieve_relevant_products, TFIDFRetriever

MOCK_PRODUCTS = [
    {
        "id": 1,
        "name": "AI Customer Support Platform",
        "category": "Customer Support",
        "description": "Omnichannel AI bot and ticketing system.",
        "features": ["Automated chat ticket resolution", "Sentiment analysis"],
        "solution": "Reduces support wait times by 80%."
    },
    {
        "id": 2,
        "name": "CRM Automation Suite",
        "category": "Sales & CRM",
        "description": "Pipeline tracking and contact enrichment.",
        "features": ["Deal lifecycle tracking", "Email sync"],
        "solution": "Accelerates B2B deal closing cycles."
    },
    {
        "id": 3,
        "name": "Cybersecurity Monitoring Platform",
        "category": "Cybersecurity",
        "description": "SIEM and threat intelligence platform.",
        "features": ["Continuous endpoint monitoring", "Ransomware detection"],
        "solution": "Protects against cyber intrusions."
    }
]

def test_retriever_selects_support():
    retriever = TFIDFRetriever(MOCK_PRODUCTS)
    results = retriever.query("We need automated ticketing and customer support chat", top_k=2)
    assert len(results) == 2
    assert results[0]["name"] == "AI Customer Support Platform"
    assert results[0]["score"] > 0

def test_retriever_selects_security():
    retriever = TFIDFRetriever(MOCK_PRODUCTS)
    results = retriever.query("Protecting our servers from ransomware and cyber attacks", top_k=2)
    assert len(results) == 2
    assert results[0]["name"] == "Cybersecurity Monitoring Platform"
    assert results[0]["score"] > 0

def test_retriever_handles_empty_query():
    retriever = TFIDFRetriever(MOCK_PRODUCTS)
    results = retriever.query("", top_k=2)
    assert len(results) <= 2

def test_retriever_with_db():
    results = retrieve_relevant_products("CRM pipeline deal closing", top_k=3)
    assert len(results) <= 3
    assert any("CRM" in r["name"] or "Sales" in r["name"] for r in results)
