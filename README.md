- create a database on your postgres named "ai_travel"
- you can run the app with
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2


cd backend
python -m app.rag.ingest


# Installation & Setup
clone the repository

## Backend
navigate to the backend/ folder
`cd backend`

duplicate the .env.example file and rename it to .env
edit your values there

setup your pgvector database:
- pull this image: https://hub.docker.com/r/pgvector/pgvector
- start pgvector container with the port 5432 and environment variables below (or edit your .env file):
    - POSTGRES_USER: user
    - POSTGRES_PASSWORD: pass
    - POSTGRES_DB: ai_travel
- Add chunks & documents tables to your database:
    - connect to your pgvector container via Exec/Bash
    - execute `psql -U <user> -d ai_travel`
    - paste the queries from backend/app/rag/schema.sql

setup your python environment
    - make sure you're still in the backend directory
    - in your backend/ directory create a virtual env example `python -m venv venv` (prefered python 3.10)
    - activate your venv and install all requirements
        Windows: `./venv/Scripts/activate`
        Linux: `source ./venv/bin/activate`
        `pip install -r requirements.txt`
        `pip install "psycopg[binary,pool]"`

populate your vector store:
    - make sure again you're still in the backend directory and your venv is activated
    - add a new folder backend/app/rag/data/ where all your pdf documents shall go
    - execute `python -m app.rag.ingest`

run your backend
    - make sure again you're still in the backend directory and your venv is activated
    - run `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2`
    - in the first execution your other tables shall be created automatically (saved_trips, users)

## Frontend
open a new terminal instance
navigate to the frontend/ folder
`cd frontend`

install node modules
`npm install`

Run the app
`npm run start`
