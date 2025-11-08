CREATE EXTENSION IF NOT EXISTS vector;

-- Simple doc and chunk tables
CREATE TABLE IF NOT EXISTS documents (
  id           SERIAL PRIMARY KEY,
  city         TEXT NOT NULL,      -- from PDF title (normalized)
  title        TEXT NOT NULL,
  created_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
  id           BIGSERIAL PRIMARY KEY,
  doc_id       INT REFERENCES documents(id) ON DELETE CASCADE,
  city         TEXT NOT NULL,
  section      TEXT,
  chunk_idx    INT NOT NULL,
  content      TEXT NOT NULL,
  tokens       INT,
  embedding    VECTOR(1536)        -- matches text-embedding-3-small
);

CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(doc_id);
CREATE INDEX IF NOT EXISTS idx_chunks_city ON chunks(city);

-- pgvector IVFFlat for cosine
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_ivfflat
ON chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

ANALYZE chunks;
