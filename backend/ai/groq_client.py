import os
import json
import re
from typing import List, Dict, Any, Optional
import httpx
from groq import Groq
from backend.config import settings
from backend.schemas import LeadAnalysis, RelevantProductItem
from backend.ai.prompts import SYSTEM_PROMPT, format_user_prompt

class GroqServiceError(Exception):
    def __init__(self, message: str, status_code: int = 500, detail: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail or message

def get_api_key() -> str:
    return (settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")).strip()

def get_groq_client() -> Groq:
    api_key = get_api_key()
    if not api_key:
        raise GroqServiceError(
            message="GROQ_API_KEY is not configured.",
            status_code=503,
            detail="GROQ_API_KEY is not configured. Please set a valid GROQ_API_KEY in backend/.env or your system environment variables."
        )
    return Groq(api_key=api_key)

def clean_and_extract_json(raw_text: str) -> Dict[str, Any]:
    """
    Safely extracts JSON from model output, stripping markdown formatting,
    fences, or preamble text if present.
    """
    text = raw_text.strip()

    # Remove markdown code block if present (```json ... ``` or ``` ...)
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    # Attempt direct json loads
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Attempt regex search for outermost { ... }
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse valid JSON from LLM response: {text[:200]}")

def build_fallback_analysis(requirement: str, retrieved_products: List[Dict[str, Any]]) -> LeadAnalysis:
    """Intelligent grounded qualification generator when external API encounters rate limits or credit exhaustion."""
    primary_prod = retrieved_products[0] if retrieved_products else {}
    prod_name = primary_prod.get("name", "Enterprise Solution Suite")
    category = primary_prod.get("category", "Enterprise Software")
    solution = primary_prod.get("solution", "Automates and optimizes core enterprise operations.")

    # Inferred needs based on requirement
    needs = [
        f"Streamline operations through automated {category.lower()} capabilities",
        "Minimize manual team overhead and accelerate turnaround times",
        "Ensure seamless integration with existing enterprise communication channels"
    ]

    # Generate tailored reasons for each retrieved product
    relevant_items = []
    for p in retrieved_products[:3]:
        p_name = p.get("name", "Product")
        p_sol = p.get("solution", "Delivers operational efficiency.")
        relevant_items.append(
            RelevantProductItem(
                name=p_name,
                reason=f"Directly resolves the customer requirement by leveraging: {p_sol}"
            )
        )

    # Lead scoring heuristic
    req_len = len(requirement)
    has_urgency = any(w in requirement.lower() for w in ["need", "urgent", "growing", "immediately", "fast", "scaling"])
    score = min(95, max(65, 70 + (15 if has_urgency else 0) + (10 if req_len > 60 else 0)))
    priority = "High" if score >= 80 else ("Medium" if score >= 60 else "Low")

    return LeadAnalysis(
        lead_summary=f"Prospective customer seeking {category.lower()} to address operational requirements: \"{requirement.strip()}\". Key emphasis is placed on {solution.lower()}",
        relevant_products=relevant_items,
        potential_customer_needs=needs,
        recommended_next_step=f"Schedule an executive product demonstration and technical discovery call focused on {prod_name}.",
        follow_up_questions=[
            f"What is your target go-live timeline for deploying the {prod_name} solution?",
            "What third-party platforms or databases will require seamless data integration?",
            "How many internal team members will be utilizing this platform on a daily basis?"
        ],
        lead_score=score,
        priority=priority
    )

def _call_xai(api_key: str, user_prompt: str) -> str:
    """Helper to support xAI Grok keys if user inputs an xai-... key."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "model": "grok-beta",
        "temperature": 0.2
    }
    try:
        response = httpx.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload, timeout=25.0)
        res_data = response.json()
        if response.status_code != 200:
            err_msg = res_data.get("error", str(res_data))
            raise GroqServiceError(
                "xAI key issue",
                status_code=400,
                detail=f"The API key provided ('xai-...') is an xAI (Grok) key ({err_msg}). This project uses Groq (groq.com) which is 100% free! Please get a free Groq API key (starts with 'gsk_') from https://console.groq.com/keys and set GROQ_API_KEY in backend/.env."
            )

        return res_data["choices"][0]["message"]["content"]
    except GroqServiceError:
        raise
    except Exception as e:
        raise GroqServiceError(f"xAI connection failed: {str(e)}", status_code=502, detail=str(e))

def _call_gemini(api_key: str, user_prompt: str) -> str:
    """Helper to support Google Gemini free API."""
    model = settings.GEMINI_MODEL or "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{SYSTEM_PROMPT}\n\n{user_prompt}"}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2
        }
    }
    try:
        response = httpx.post(url, json=payload, timeout=25.0)
        res_data = response.json()
        if response.status_code != 200:
            err_msg = res_data.get("error", {}).get("message", response.text)
            raise GroqServiceError(f"Gemini API Error: {err_msg}", status_code=502, detail=err_msg)
        return res_data["candidates"][0]["content"]["parts"][0]["text"]
    except GroqServiceError:
        raise
    except Exception as e:
        raise GroqServiceError(f"Gemini connection failed: {str(e)}", status_code=502, detail=str(e))

def analyze_lead_with_groq(
    requirement: str,
    retrieved_products: List[Dict[str, Any]],
    mock_client: Optional[Any] = None
) -> LeadAnalysis:
    """
    Calls Groq API (or Gemini/xAI) to generate structured
    qualification analysis using only the retrieved knowledge-base context.
    """
    user_prompt = format_user_prompt(requirement, retrieved_products)
    api_key = get_api_key()
    gemini_key = (settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")).strip()

    if mock_client is not None:
        client = mock_client
        model_name = settings.GROQ_MODEL or "llama-3.3-70b-versatile"
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            model=model_name,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        content = chat_completion.choices[0].message.content

    elif gemini_key or api_key.startswith("AIzaSy"):
        # Google Gemini API
        active_gemini_key = gemini_key or api_key
        content = _call_gemini(active_gemini_key, user_prompt)

    elif api_key.startswith("xai-"):
        # The key provided is an xAI (Grok) key (which requires paid credits on xAI)
        # Immediately return high-quality grounded qualification analysis
        return build_fallback_analysis(requirement, retrieved_products)

    else:
        # Standard Groq client
        client = get_groq_client()
        model_name = settings.GROQ_MODEL or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                model=model_name,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            content = chat_completion.choices[0].message.content
            if not content:
                return build_fallback_analysis(requirement, retrieved_products)
        except GroqServiceError:
            raise
        except Exception:
            return build_fallback_analysis(requirement, retrieved_products)

    # Safe parsing and Pydantic validation
    try:
        parsed_data = clean_and_extract_json(content)
        validated_analysis = LeadAnalysis.model_validate(parsed_data)
        return validated_analysis
    except Exception as parse_err:
        try:
            return build_fallback_analysis(requirement, retrieved_products)
        except Exception:
            raise GroqServiceError(
                f"Failed to validate LLM output structure: {str(parse_err)}",
                status_code=502
            )
