from typing import List, Tuple, Optional
from pgvector import Vector
from .db import get_conn
from .embedder import embed_texts
from .splitter import normalize_city

Row = Tuple[int, str, str, int, str, float]  # id, city, section, chunk_idx, content, distance

def _pg_search(query_vec, city: Optional[str], top_n=12) -> List[Row]:
    sql = """
    SELECT id, city, section, chunk_idx, content,
           (embedding <=> %s::vector) AS distance
    FROM chunks
    {where}
    ORDER BY embedding <=> %s::vector
    LIMIT %s;
    """
    where = "WHERE city = %s" if city else ""
    with get_conn() as conn, conn.cursor() as cur:
        if city:
            cur.execute(sql.format(where=where), (query_vec, normalize_city(city), query_vec, top_n))
        else:
            cur.execute(sql.format(where=where), (query_vec, query_vec, top_n))
        return cur.fetchall()

def mmr(candidates: List[Row], k=4, lambda_mult=0.5) -> List[Row]:
    if len(candidates) <= k:
        return candidates
    selected: List[Row] = []
    while len(selected) < k:
        best, best_score = None, None
        for c in candidates:
            if c in selected: 
                continue
            relevance = -c[-1]  # smaller distance → better
            diversity_penalty = 0.0
            for s in selected:
                same_section = 1.0 if c[2] == s[2] else 0.0
                close_idx = 1.0 if abs(c[3]-s[3]) <= 1 and c[1]==s[1] else 0.0
                diversity_penalty = max(diversity_penalty, 0.6*same_section + 0.4*close_idx)
            score = lambda_mult*relevance - (1-lambda_mult)*diversity_penalty
            if best_score is None or score > best_score:
                best_score, best = score, c
        selected.append(best)
    return selected

def retrieve(query: str, city: Optional[str] = None, k=4) -> List[Row]:
    qvec = Vector(embed_texts([query])[0])
    cands = _pg_search(qvec, city, top_n=12)
    return mmr(cands, k=k)
