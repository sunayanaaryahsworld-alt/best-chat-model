import asyncio
import logging
import time
from typing import Optional

import router.usage_tracker as usage_tracker
from router.config import MODEL_PRIORITY, ROUTER_MODE
from router.evaluator import pick_best

# ─── Logger ──────────────────────────────────────────────────────────────────
logger = logging.getLogger("router")

# ─── Model registry ──────────────────────────────────────────────────────────
# Maps short name → module.ask_model callable.
# Import lazily inside functions to avoid crashing at startup when optional
# dependencies are not installed for unused models.

def _load_model(name: str):
    """Dynamically import and return the ask_model function for `name`."""
    import importlib
    # module_map = {
    #     "groq":        "models.groq_model",
    #     "openrouter":  "models.openrouter_model",
    # }
    module_map = {
    "groq": "router.models.groq_model",
    "openrouter": "router.models.openrouter_model",
}
    if name not in module_map:
        raise ValueError(f"Unknown model name: '{name}'")
    module = importlib.import_module(module_map[name])
    return module.ask_model


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _call_model_sync(name: str, prompt: str) -> Optional[str]:
    """
    Call a single model synchronously.
    Returns the response string on success, or None on any error.
    Records stats in usage_tracker.
    """
    try:
        ask_fn = _load_model(name)
    except (ValueError, ImportError) as exc:
        logger.warning("[%s] Could not load model: %s", name, exc)
        usage_tracker.record_failure(name, str(exc))
        return None

    start = time.monotonic()
    try:
        response = ask_fn(prompt)
        latency = (time.monotonic() - start) * 1000
        usage_tracker.record_success(name, latency)
        logger.info("[%s] ✓ responded in %.0f ms", name, latency)
        return response
    except Exception as exc:
        latency = (time.monotonic() - start) * 1000
        usage_tracker.record_failure(name, str(exc))
        logger.warning("[%s] ✗ failed after %.0f ms — %s", name, latency, exc)
        return None


async def _call_model_async(name: str, prompt: str) -> tuple[str, Optional[str]]:
    """Async wrapper so we can run models concurrently in 'best' mode."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _call_model_sync, name, prompt)
    return name, result


# ─── Public API ───────────────────────────────────────────────────────────────

def route(prompt: str) -> dict:
    """
    Route a prompt through the configured LLM models.

    Returns a dict:
    {
        "response": str,
        "model_used": str,
        "mode": str,
        "tried": [str],          # models attempted
        "failed": [str],         # models that failed
    }
    Raises RuntimeError if every model (including Ollama) fails.
    """
    mode = ROUTER_MODE.lower()

    if mode == "best":
        return _route_best(prompt)
    else:
        return _route_fallback(prompt)


def _route_fallback(prompt: str) -> dict:
    """
    Try models in MODEL_PRIORITY order.
    Return the first successful response.
    Ollama is always the final safety net.
    """
    priority = list(MODEL_PRIORITY)

    tried = []
    failed = []

    for name in priority:
        tried.append(name)
        response = _call_model_sync(name, prompt)
        if response:
            return {
                "response": response,
                "model_used": name,
                "mode": "fallback",
                "tried": tried,
                "failed": failed,
            }
        failed.append(name)

    raise RuntimeError(
        f"All models failed. Tried: {tried}. Check logs for details."
    )


def _route_best(prompt: str) -> dict:
    """
    Query all models concurrently and return the highest-scored response.
    Falls back to Ollama if all concurrent calls fail.
    """
    priority = list(MODEL_PRIORITY)

    async def _gather():
        tasks = [_call_model_async(name, prompt) for name in priority]
        return await asyncio.gather(*tasks)

    # Run the async gather from sync context
    results = asyncio.run(_gather())

    tried = priority
    successes = {name: resp for name, resp in results if resp}
    failed = [name for name, resp in results if not resp]

    if not successes:
        raise RuntimeError(
            f"All models failed in best-model mode. Tried: {tried}."
        )

    best_name, best_response = pick_best(successes)
    logger.info("[router] best-mode winner: %s", best_name)

    return {
        "response": best_response,
        "model_used": best_name,
        "mode": "best",
        "tried": tried,
        "failed": failed,
    }
    
    
def route_stream(prompt: str):
    """
    Try Groq streaming first.
    If Groq fails/quota over, fall back to OpenRouter (non-stream).
    Yields tokens.
    """
    # Try Groq stream first
    try:
        from router.models.groq_model import ask_model_stream
        token_count = 0
        for token in ask_model_stream(prompt):
            token_count += 1
            yield token
        return  # Groq succeeded, done
    except Exception as e:
        logger.warning("[groq] stream failed, falling back to openrouter: %s", e)

    # Groq failed → fallback to OpenRouter (yields full response at once)
    try:
        from router.models.openrouter_model import ask_model
        response = ask_model(prompt)
        yield response
    except Exception as e:
        logger.warning("[openrouter] also failed: %s", e)
        yield "Sorry, AI temporarily unavailable."    