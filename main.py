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
from fastapi import Body

import router as llm_router
import usage_tracker

ALLOWED_TOPICS = [
    "salon","spa","hair","hairstyle","haircut",
    "beauty","facial","skin","skincare",
    "makeup","nail","massage","grooming",
    "barber","trend","style",
    "pimple","pimples","acne","face","glow"
]
GREETING_WORDS = [
    "hi",
    "hello",
    "hey",
    "hii",
    "good morning",
    "good evening",
    "good afternoon"
]

def is_allowed_question(text: str) -> bool:

    text = text.lower()

    # allow greetings
    for g in GREETING_WORDS:
        if g in text:
            return True

    # allow salon topics
    for word in ALLOWED_TOPICS:
        if word in text:
            return True

    return False
    
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

@app.get("/stats", tags=["System"])
def stats():
    """Return per-model usage statistics."""
    return usage_tracker.get_stats()


@app.post("/stats/reset", tags=["System"])
def reset_stats():
    """Reset all usage statistics."""
    usage_tracker.reset_stats()
    return {"status": "stats reset"}

@app.post("/chat")
def chat(data: dict = Body(...)):

    prompt = data.get("message", "")

    if not prompt:
        raise HTTPException(status_code=400, detail="Empty message")

    # ✅ restrict domain
    if not is_allowed_question(prompt):

        return {
            "response": "I can only answer questions related to salon, spa, beauty, hairstyle, skincare, or grooming.",
            "model_used": "filter"
        }

    # ✅ call router
    short_prompt = f"""
    You are a salon and beauty assistant.
    
    STRICT RULES:
    - Answer in maximum 2 lines only
    - No bullet points
    - No long explanations
    - Keep it simple and direct
    
    Question: {prompt}
"""

    result = llm_router.route(short_prompt)
    result["response"] = result["response"].split("\n")[0][:200]    
    
    return result
    
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