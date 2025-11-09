from __future__ import annotations
import json
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from ..agent.graph import app_graph

router = APIRouter(prefix="/api/agent", tags=["agent"])

class AgentQuery(BaseModel):
    question: str
    city: Optional[str] = None
    days: int = 3  # optional hint for itinerary length

@router.post("/query")
async def agent_query(payload: AgentQuery) -> Dict[str, Any]:
    """
    Orchestrated agent call.
    Returns a structured JSON object {city, recommendations[], forecast?, itinerary?, sources{}}.
    """
    # Compose a focused user message that hints the agent to call tools and output JSON
    city_hint = f"City: {payload.city}" if payload.city else "City: (unspecified)"
    ask = (
        f"{city_hint}\n"
        f"User question: {payload.question}\n"
        f"If an itinerary is relevant, make it {payload.days} day(s)."
    )

    state = {"messages": [HumanMessage(content=ask)]}
    result = app_graph.invoke(state)
    last = result["messages"][-1]
    text = getattr(last, "content", "")

    # Must be a JSON object per system prompt; fall back gracefully if not
    try:
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("Non-object JSON")
        return data
    except Exception:
        # Fallback wrapper
        return {
            "city": payload.city or "unknown",
            "recommendations": [text] if text else [],
            "forecast": None,
            "itinerary": [],
            "sources": {"rag": [], "weather": []},
            "_note": "Model returned non-JSON; wrapped as text."
        }
