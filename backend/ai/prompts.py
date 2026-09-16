import json
from typing import List, Dict, Any

SYSTEM_PROMPT = """You are an expert AI Sales Lead Qualification Assistant.
Your job is to analyze potential customer requirements and qualify the sales lead based EXCLUSIVELY on the retrieved knowledge-base products provided to you.

CRITICAL RULES:
1. Grounding: You must ONLY reference products and features present in the provided retrieved knowledge-base context. Do NOT invent, hallucinate, or recommend external products that are not in the context.
2. Objectivity: Assess the customer's problem accurately and map specific capabilities of the retrieved products to their needs.
3. Structured Output: You MUST respond ONLY with a valid JSON object. Do not include markdown code block formatting (like ```json), commentary, or extra text before or after the JSON.

JSON SCHEMA:
{
  "lead_summary": "A 2-3 sentence executive summary qualifying this lead, their industry context, and pain points.",
  "relevant_products": [
    {
      "name": "Exact Name of Product from Context",
      "reason": "Clear explanation of how this product's features specifically resolve the customer's stated requirement."
    }
  ],
  "potential_customer_needs": [
    "Identified or inferred need 1",
    "Identified or inferred need 2"
  ],
  "recommended_next_step": "Specific, actionable next sales step (e.g., technical demo, security architecture review, trial onboarding).",
  "follow_up_questions": [
    "Targeted discovery question 1",
    "Targeted discovery question 2",
    "Targeted discovery question 3"
  ],
  "lead_score": 85,
  "priority": "High"
}

Scoring Guidelines:
- lead_score (integer 0 to 100): Evaluate budget/scale indicators, urgency, clarity of need, and alignment with retrieved products.
- priority: "High" (score >= 75), "Medium" (score 45-74), "Low" (score < 45).
"""

def format_user_prompt(requirement: str, retrieved_products: List[Dict[str, Any]]) -> str:
    """Formats the user prompt with the customer requirement and retrieved context."""
    context_blocks = []
    for idx, p in enumerate(retrieved_products, start=1):
        features_str = ", ".join(p.get("features", [])) if isinstance(p.get("features"), list) else str(p.get("features", ""))
        block = (
            f"Product {idx}: {p.get('name')}\n"
            f"Category: {p.get('category')}\n"
            f"Description: {p.get('description')}\n"
            f"Features: {features_str}\n"
            f"Target Solution: {p.get('solution')}\n"
            f"Relevance Score: {p.get('score', 'N/A')}"
        )
        context_blocks.append(block)

    context_text = "\n\n".join(context_blocks)

    return f"""CUSTOMER REQUIREMENT:
\"\"\"{requirement}\"\"\"

RETRIEVED KNOWLEDGE BASE CONTEXT (Top {len(retrieved_products)} Matches):
\"\"\"
{context_text}
\"\"\"

Analyze this customer requirement against the retrieved knowledge base context. Return ONLY the qualified lead analysis in the requested JSON format."""
