from fastapi import FastAPI

app = FastAPI(title="SUTMS API", version="0.1.0")


@app.get("/health")
def health_check():
    """Basic liveness check -- useful for Week 1 demo and CI."""
    return {"status": "ok"}


