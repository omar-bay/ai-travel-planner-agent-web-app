from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["rag"])

@router.post("/rag-search")
async def rag_search(query: dict):
    # TODO: implement pgvector similarity search
    return {"chunks": [], "meta": {}}