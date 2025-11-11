# app/agent/tools.py
from typing import TypedDict
import requests
from langchain_core.tools import tool
from ..core.config import settings
import json
import re
import os

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


JINA_API_KEY = os.getenv("JINA_API_KEY")

def _headers(extra=None):
    h = {"Authorization": f"Bearer {JINA_API_KEY}"} if JINA_API_KEY else {}
    if extra:
        h.update(extra)
    return h

def _format_search_md(items):
    lines = []
    for i, it in enumerate(items, start=1):
        title = it.get("title") or it.get("page_title") or "Untitled"
        url = it.get("url") or it.get("link") or it.get("source") or ""
        desc = it.get("description") or it.get("snippet") or it.get("content") or ""
        date = it.get("published_time") or it.get("date") or it.get("publishedAt") or ""
        if isinstance(desc, dict):
            desc = desc.get("text") or ""
        if desc and len(desc) > 500:
            desc = desc[:500].rstrip() + "…"
        lines.append(f"[{i}] Title: {title}")
        if url:
            lines.append(f"[{i}] URL Source: {url}")
        if desc:
            lines.append(f"[{i}] Description: {desc}")
        if date:
            lines.append(f"[{i}] Date: {date}")
        lines.append("")
    return "\n".join(lines).strip()

def _extract_urls_from_md(md: str):
    urls = re.findall(r"URL Source:\s*(https?://\S+)", md)
    urls += re.findall(r"(https?://[^\s)]+)", md)
    seen, ordered = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u); ordered.append(u)
    return ordered

@tool("web_search", return_direct=False)
def web_search(query: str, top_k: int = 5) -> str:
    """
    Search the web via Jina Search and return a markdown list:
    [i] Title: ...
    [i] URL Source: ...
    [i] Description: ...
    [i] Date: ...
    """
    if not JINA_API_KEY:
        return "❌ Missing JINA_API_KEY env variable."
    url = f"https://s.jina.ai/?q={requests.utils.quote(query)}"
    headers = _headers({"X-Respond-With": "no-content"})
    r = requests.get(url, headers=headers, timeout=60)
    r.raise_for_status()
    try:
        data = r.json()
        items = data.get("data") or data.get("results") or data
        if isinstance(items, dict):
            items = [items]
        if not isinstance(items, list):
            items = []
    except json.JSONDecodeError:
        return r.text
    items = items[: max(1, int(top_k))]
    return _format_search_md(items)

@tool("web_read", return_direct=False)
def web_read(url: str) -> str:
    """Read a webpage using Jina Read-the-Web; returns markdown/plain text."""
    if not JINA_API_KEY:
        return "❌ Missing JINA_API_KEY env variable."
    if url.startswith("http://") or url.startswith("https://"):
        endpoint = f"https://r.jina.ai/{url}"
    else:
        endpoint = f"https://r.jina.ai/https://{url}"
    r = requests.get(endpoint, headers=_headers(), timeout=60)
    r.raise_for_status()
    return r.text

@tool("extract_urls_from_markdown", return_direct=True)
def extract_urls_from_markdown(markdown_text: str) -> str:
    """Return a JSON array of URLs found in web_search markdown output."""
    urls = _extract_urls_from_md(markdown_text)
    return json.dumps(urls)

TOOLS = [rag_search, city_weather, web_search, extract_urls_from_markdown, web_read]
