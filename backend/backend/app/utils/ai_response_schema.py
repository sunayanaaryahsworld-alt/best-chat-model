def ai_response(
    reply_text: str,
    intent: str = "general",
    confidence: float = 0.9,
    meta: dict | None = None
):
    return {
        "reply_text": reply_text,
        "intent": intent,
        "confidence": confidence,
        "meta": meta or {}
    }
