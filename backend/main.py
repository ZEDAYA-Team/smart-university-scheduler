import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.database.seed import seed_development_data
from app.routes import (
    setup_router,
    offerings_router,
    lecturer_availability_router,
    conflicts_router,
)

app = FastAPI(title="SUTMS API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])

# Remove tags=["setup"] so individual resource tags ("Departments", "Rooms", etc.) can render
app.include_router(setup_router, prefix="/api/setup")

# These three were built but never mounted -- each router already carries
# its own full path segment (/offerings, /lecturers/{id}/availability,
# /conflicts), so they all just need the shared /api prefix, not /api/setup.
app.include_router(offerings_router, prefix="/api")
app.include_router(lecturer_availability_router, prefix="/api")
app.include_router(conflicts_router, prefix="/api")

@app.on_event("startup")
def seed_data() -> None:
    if os.getenv("SEED_DEMO_DATA", "false").lower() == "true":
        seed_development_data()

@app.get("/health")
def health_check():
    """Basic liveness check -- useful for Week 1 demo and CI."""
    return {"status": "ok"}