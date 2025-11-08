import psycopg
from pgvector.psycopg import register_vector
from ..core.config import settings

def get_conn():
    dsn = settings.DATABASE_URL.replace("+asyncpg", "")
    conn = psycopg.connect(dsn, autocommit=True)
    register_vector(conn)
    return conn
