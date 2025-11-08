import os
from pathlib import Path
from .db import get_conn
from .splitter import section_aware_split
from .embedder import embed_texts
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

DATA_DIR = Path(__file__).parent / "data"  # ./rag/data/

def token_len(t: str) -> int:
    return len(enc.encode(t))

def ingest_pdf(pdf_path: str):
    """Ingest a single PDF file into the pgvector database."""
    city, title, chunks = section_aware_split(pdf_path)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO documents (city, title) VALUES (%s, %s) RETURNING id;", (city, title))
        doc_id = cur.fetchone()[0]

        contents = [c[2] for c in chunks]
        embeddings = embed_texts(contents)

        for (section, idx, content), emb in zip(chunks, embeddings):
            cur.execute("""
                INSERT INTO chunks (doc_id, city, section, chunk_idx, content, tokens, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (doc_id, city, section, idx, content, token_len(content), emb))
    return {"doc_id": doc_id, "city": city, "title": title, "chunks": len(chunks)}


def ingest_all_pdfs(data_dir: Path = DATA_DIR):
    """Scan ./rag/data/ for all PDFs and ingest them."""
    pdf_files = sorted(p for p in data_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {data_dir}")
        return

    print(f"Found {len(pdf_files)} PDF(s) in {data_dir}")
    summary = []
    for pdf in pdf_files:
        print(f"→ Ingesting: {pdf.name}")
        try:
            res = ingest_pdf(str(pdf))
            summary.append(res)
            print(f"   ✅ {res['city']} ({res['chunks']} chunks)")
        except Exception as e:
            print(f"   ❌ Failed: {pdf.name} → {e}")

    print("\n=== Ingestion Summary ===")
    for s in summary:
        print(f"{s['city']:15} {s['chunks']:5} chunks | {s['title']}")
    print(f"\nTotal PDFs ingested: {len(summary)}")


if __name__ == "__main__":
    ingest_all_pdfs()
