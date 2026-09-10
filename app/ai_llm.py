import json
import re
from typing import Any
import httpx
from .config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL


def llm_enabled() -> bool:
    return bool(LLM_API_KEY and LLM_MODEL)


def _endpoint() -> str:
    base = (LLM_BASE_URL or "https://api.openai.com/v1").rstrip("/")
    return base if base.endswith("/responses") else base + "/responses"


def _extract_text(data: dict) -> str:
    if isinstance(data.get("output_text"), str):
        return data["output_text"]
    chunks = []
    for item in data.get("output", []):
        for content in item.get("content", []) if isinstance(item, dict) else []:
            if content.get("type") == "output_text":
                chunks.append(content.get("text", ""))
    return "".join(chunks).strip()


def _json_from_text(text: str) -> Any:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def responses_text(instructions: str, user_input: str, max_output_tokens: int = 900) -> str:
    if not llm_enabled():
        raise RuntimeError("LLM is not configured")
    payload = {
        "model": LLM_MODEL,
        "instructions": instructions,
        "input": user_input,
        "max_output_tokens": max_output_tokens,
        "store": False,
    }
    headers = {"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"}
    with httpx.Client(timeout=45.0) as client:
        response = client.post(_endpoint(), headers=headers, json=payload)
        response.raise_for_status()
        return _extract_text(response.json())


def polish_itinerary(plan: dict, req: Any) -> dict:
    """Use the LLM only to enrich grounded itinerary content; database facts remain authoritative."""
    if not llm_enabled():
        return plan
    compact = {
        "destination": plan["destination"],
        "days": plan["days"],
        "estimated_total": plan["estimated_total"],
        "budget": plan["budget"],
        "sustainability_score": plan["sustainability_score"],
    }
    instructions = (
        "You are SMARTTOUR AI, a tourism planning copilot. Rewrite the supplied itinerary into concise, "
        "natural travel guidance. Do not invent attractions, prices, crowd values, safety scores, restaurants, "
        "times, or availability. Those fields are database facts and must remain unchanged. Return JSON only with "
        "keys ai_summary (string), ai_tips (array of strings), and item_reasons (object mapping exact attraction "
        "title to a one-sentence reason). Keep reasons grounded in the supplied data."
    )
    user = json.dumps({"traveler_profile": req.model_dump(), "grounded_plan": compact}, ensure_ascii=False)
    try:
        data = _json_from_text(responses_text(instructions, user, 700))
        plan["ai_summary"] = str(data.get("ai_summary", "")).strip()
        plan["ai_tips"] = [str(x) for x in data.get("ai_tips", [])][:5]
        reasons = data.get("item_reasons", {}) if isinstance(data.get("item_reasons"), dict) else {}
        for day in plan.get("days", []):
            for item in day.get("items", []):
                if item.get("title") in reasons and reasons[item["title"]]:
                    item["reason"] = reasons[item["title"]]
        plan["ai_provider"] = "OpenAI Responses API"
        plan["ai_model"] = LLM_MODEL
    except Exception:
        plan["ai_provider"] = "SmartTour deterministic fallback"
    return plan


def answer_with_llm(message: str, destination: str, context: dict) -> str | None:
    if not llm_enabled():
        return None
    instructions = (
        "You are the SMARTTOUR AI travel assistant. Answer using only the supplied tourism context. "
        "Be concise, practical, and transparent. Do not claim live weather, traffic, availability, emergency "
        "status, or booking confirmation unless present in context. If data is missing, say so. Prefer local "
        "businesses and lower-crowd alternatives when suitable."
    )
    user = json.dumps({"destination": destination, "question": message, "tourism_context": context}, ensure_ascii=False)
    try:
        return responses_text(instructions, user, 500)
    except Exception:
        return None
