import json, requests
from tenacity import retry, wait_exponential, stop_after_attempt
from ..core.config import settings

OPENAI_BASE = "https://api.openai.com/v1"
EMBED_MODEL = "text-embedding-3-small"  # 1536-dim

@retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(6))
def embed_texts(texts: list[str]) -> list[list[float]]:
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"model": EMBED_MODEL, "input": texts}
    r = requests.post(f"{OPENAI_BASE}/embeddings", headers=headers, data=json.dumps(payload), timeout=60)
    r.raise_for_status()
    data = r.json()
    return [d["embedding"] for d in data["data"]]
