from __future__ import annotations

import os
from pydantic import BaseModel
from typing import Any, Dict, Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from starlette.concurrency import run_in_threadpool

from ..rag.ingest import ingest_pdf
from ..rag.retrieve import retrieve
from ..rag.answer import synthesize_answer
from ..rag.splitter import normalize_city

router = APIRouter(prefix="/api", tags=["rag"])

@router.post("/rag-ingest")
async def rag_ingest(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Ingest a single PDF city guide:
    - Splits by template sections, chunks with overlap
    - Embeds via OpenAI (text-embedding-3-small)
    - Inserts into Postgres + pgvector
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")
    tmp_path = f"/tmp/{file.filename}"
    # save
    with open(tmp_path, "wb") as f:
        f.write(await file.read())
    try:
        res = await run_in_threadpool(ingest_pdf, tmp_path)
        return {"status": "ok", **res}
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


class RAGSearchRequest(BaseModel):
    question: str
    city: Optional[str] = None
    k: int = 4
    with_answer: bool = True

@router.post("/rag-search")
async def rag_search(req: RAGSearchRequest) -> Dict[str, Any]:
    """
    JSON-based RAG search endpoint.
    Example JSON:
    {
      "question": "Best food in Tokyo?",
      "city": "tokyo",
      "k": 4,
      "with_answer": true
    }
    """
    city_norm = normalize_city(req.city) if req.city else None
    rows = await run_in_threadpool(retrieve, req.question, city_norm, req.k)
    chunks = [
        {
            "id": r[0],
            "city": r[1],
            "section": r[2],
            "chunk_idx": r[3],
            "content": r[4],
            "distance": float(r[5]),
        }
        for r in rows
    ]

    out: Dict[str, Any] = {"chunks": chunks}

    if req.with_answer and chunks:
        contexts = [{"section": c["section"], "content": c["content"]} for c in chunks]
        ans = await run_in_threadpool(synthesize_answer, req.question, req.city, contexts)
        out["answer"] = ans

    return out
