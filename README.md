- create a database on your postgres named "ai_travel"
- you can run the app with
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2


cd backend
python -m app.rag.ingest