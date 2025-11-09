from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# adjust these to your actual project paths
from ..dependencies.auth import get_db

router = APIRouter(prefix="/api", tags=["cities"])
bearer_scheme = HTTPBearer(auto_error=True)


def _ensure_authenticated(creds: HTTPAuthorizationCredentials) -> str:
    """Simple Bearer token check — replace with real JWT verification if needed."""
    if not creds or not creds.scheme.lower() == "bearer" or not creds.credentials:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return creds.credentials


@router.get("/cities", summary="List distinct city/title pairs from documents")
async def list_cities(
    q: Optional[str] = Query(None, description="Search by city or title (case-insensitive)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Dict[str, Any]:
    _ensure_authenticated(creds)

    where_clauses = [
        "city IS NOT NULL",
        "title IS NOT NULL",
        "TRIM(city) <> ''",
        "TRIM(title) <> ''",
    ]
    params: Dict[str, Any] = {"limit": limit, "offset": offset}

    if q:
        where_clauses.append("(LOWER(city) LIKE :q OR LOWER(title) LIKE :q)")
        params["q"] = f"%{q.lower()}%"

    where_sql = " AND ".join(where_clauses)

    page_sql = text(f"""
        SELECT city, title
        FROM documents
        WHERE {where_sql}
        GROUP BY city, title
        ORDER BY title ASC
        LIMIT :limit OFFSET :offset
    """)

    count_sql = text(f"""
        SELECT COUNT(*) AS cnt FROM (
            SELECT 1
            FROM documents
            WHERE {where_sql}
            GROUP BY city, title
        ) AS sub
    """)

    # ✅ use 'await' and 'scalars()' / 'mappings()' with AsyncSession
    result_page = await db.execute(page_sql, params)
    rows = result_page.mappings().all()

    result_count = await db.execute(count_sql, params)
    count_row = result_count.mappings().first()
    total = int(count_row["cnt"]) if count_row else 0

    items = [
        {
            "city": (row["city"] or "").strip().lower(),
            "title": (row["title"] or "").strip(),
        }
        for row in rows
    ]

    return {"items": items, "total": total, "limit": limit, "offset": offset}
