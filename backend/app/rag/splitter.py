from pypdf import PdfReader
import re
from pathlib import Path

TEMPLATE_SECTIONS = [
    "Overview", "History", "Orientation", "Neighborhoods",
    "Climate", "Transportation", "Things to See", "Things to Do",
    "Practical information", "Practical Information"
]

def normalize_city(name: str) -> str:
    # lowercase, remove spaces & non-alphanumerics (matches your need)
    name = name.strip().lower()
    return re.sub(r'[^a-z0-9]', '', name)

def section_aware_split(pdf_path: str, max_chunk_chars=900, overlap=120):
    reader = PdfReader(pdf_path)
    full = "\n".join(page.extract_text() or "" for page in reader.pages)

    title = next((l.strip() for l in full.splitlines() if l.strip()), "Unknown City")
    stem = Path(pdf_path).stem
    raw_city = title or stem
    city = normalize_city(raw_city)

    escaped = [re.escape(s) for s in TEMPLATE_SECTIONS]
    pat = r"(?m)^(?P<head>{})(?:\s*[:\-])?\s*$".format("|".join(escaped))
    parts, last, current = [], 0, "Overview"

    for m in re.finditer(pat, full):
        head = m.group("head")
        if m.start() > 0:
            parts.append((current, full[last:m.start()].strip()))
        current = "Practical information" if head.lower().startswith("practical") else head
        last = m.end()

    parts.append((current, full[last:].strip()))

    chunks, idx = [], 0
    for sec, text in parts:
        text = re.sub(r"\n{2,}", "\n", text).strip()
        if not text:
            continue
        start = 0
        while start < len(text):
            end = min(start + max_chunk_chars, len(text))
            chunks.append((sec, idx, text[start:end]))
            idx += 1
            if end == len(text): break
            start = max(0, end - overlap)

    return city, title, chunks
