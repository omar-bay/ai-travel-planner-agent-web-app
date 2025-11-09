import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.db import init_db
from .routers import auth as auth_router
from .routers import trips as trips_router
from .routers import weather as weather_router
from .routers import rag as rag_router
from .routers import agent as agent_router
from .routers import cities as cities_router

app = FastAPI(title="AI Travel Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await init_db()

app.include_router(auth_router.router)
app.include_router(trips_router.router)
app.include_router(weather_router.router)
app.include_router(rag_router.router)
app.include_router(agent_router.router)
app.include_router(cities_router.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)