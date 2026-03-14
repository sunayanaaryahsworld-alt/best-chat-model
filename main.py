"""
main.py
FastAPI application entry point for the Multi-LLM Smart Router Chatbot.

Endpoints:
  GET  /chat?q=<prompt>          → route prompt through LLMs
  GET  /stats                    → per-model usage statistics
  POST /stats/reset              → reset usage statistics
  GET  /health                   → liveness check
"""

import logging
import sys

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

import router as llm_router
import usage_tracker

# ─── Logging setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("main")

# ─── FastAPI app ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Multi-LLM Smart Router Chatbot",
    description=(
        "Routes prompts through multiple LLM APIs with automatic failover. "
        "Supports fallback mode (priority order) and best-model mode (concurrent scoring)."
    ),
    version="1.0.0",
)

# Allow all origins for development — restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health():
    """Simple liveness probe."""
    return {"status": "ok"}


@app.get("/chat", tags=["Chat"])
def chat(
    q: str = Query(..., description="The prompt / question to send to the LLM router"),
):
    """
    Route a prompt through the configured LLM models.

    Returns the first successful (or best-scored) response along with
    metadata about which model answered and which ones failed.
    """
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query 'q' must not be empty.")

    logger.info("Incoming query: %r", q[:120])

    try:
        result = llm_router.route(q)
        logger.info(
            "Query answered by [%s] | tried=%s | failed=%s",
            result["model_used"],
            result["tried"],
            result["failed"],
        )
        return result
    except RuntimeError as exc:
        logger.error("All models failed: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc))


@app.get("/stats", tags=["System"])
def stats():
    """Return per-model usage statistics."""
    return usage_tracker.get_stats()


@app.post("/stats/reset", tags=["System"])
def reset_stats():
    """Reset all usage statistics."""
    usage_tracker.reset_stats()
    return {"status": "stats reset"}


@app.get("/ranking")
def ranking():

    stats = usage_tracker.get_stats()

    models = []

    for name, s in stats.items():

        if s["total_calls"] == 0:
            continue

        score = s["success_rate"] - (s["avg_latency_ms"] / 1000)

        models.append({
            "model": name,
            "score": score,
            "success_rate": s["success_rate"],
            "latency": s["avg_latency_ms"],
        })

    models.sort(key=lambda x: x["score"], reverse=True)

    return models
    
# ─── Dev entrypoint ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)