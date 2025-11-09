# app/agent/tools.py
from typing import TypedDict
import requests
from langchain_core.tools import tool
from ..core.config import settings

class RAGResult(TypedDict):
    chunks: list

@tool("rag_search", return_direct=False)
def rag_search(question: str, city: str, k: int = 4, with_answer: bool = False) -> str:
    """
    Query your RAG API. Returns JSON string with 'chunks' (and possibly 'answer').
    """
    payload = {"question": question, "city": city, "k": k, "with_answer": with_answer}
    r = requests.post("http://127.0.0.1:8000/api/rag-search", json=payload, timeout=60)
    r.raise_for_status()
    return r.text

@tool("city_weather", return_direct=False)
def city_weather(city: str, past_days: int = 0, include_marine: bool = True, include_elevation: bool = False) -> str:
    """
    Fetch a human-friendly weather summary for a city (JSON string).
    """
    params = {
        "city": city,
        "past_days": past_days,
        "include_marine": str(include_marine).lower(),
        "include_elevation": str(include_elevation).lower(),
    }
    r = requests.get("http://127.0.0.1:8000/api/weather", params=params, timeout=60)
    r.raise_for_status()
    return r.text

TOOLS = [rag_search, city_weather]
