from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from .schemas import SlateInput
from .orchestrator import analyze_slate

load_dotenv()
app = FastAPI(title="QFPM Multi-Agent API", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "qfpm-multi-agent"}

@app.post("/analyze")
async def analyze(payload: SlateInput):
    if not payload.matches:
        raise HTTPException(status_code=422, detail="At least one match is required.")
    try:
        return await analyze_slate(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QFPM run failed: {type(exc).__name__}: {exc}") from exc
