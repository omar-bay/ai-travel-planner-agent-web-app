import json, requests
from ..core.config import settings

OPENAI_BASE = "https://api.openai.com/v1"
SYSTEM = (
    "You are a helpful travel assistant. Answer with concise, practical guidance. "
    "Cite neighborhoods, transit tips, and seasonal/weather caveats when relevant."
)

def synthesize_answer(question: str, city: str | None, contexts):
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    context_text = "\n\n".join(
        f"[{i+1}] Section: {c['section']}\n{c['content']}"
        for i, c in enumerate(contexts)
    )
    prompt = (
        f"City: {city or 'Unknown'}\n"
        f"User question: {question}\n\n"
        f"Use ONLY the following sources:\n{context_text}\n\n"
        f"Answer briefly. If unsure, say so."
    )
    payload = {
        "model": "gpt-4o-mini",
        "input": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt}
        ]
    }
    r = requests.post(f"{OPENAI_BASE}/responses", headers=headers, data=json.dumps(payload), timeout=120)
    r.raise_for_status()
    data = r.json()
    for out in data.get("output", []):
        if out.get("type") == "message":
            parts = out.get("content", [])
            texts = []
            for p in parts:
                if p.get("type") in ("output_text",) and "text" in p:
                    texts.append(p["text"])
                elif "text" in p:
                    texts.append(p["text"])
            return "".join(texts).strip()
    return data.get("output_text") or "[No text]"
