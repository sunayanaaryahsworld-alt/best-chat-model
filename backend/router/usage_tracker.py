"""
usage_tracker.py
Tracks per-model usage statistics in-memory (resets on restart).
For production, replace the in-memory store with Redis or a database.
"""

from collections import defaultdict
from datetime import datetime
from threading import Lock
from typing import Dict, List

# Thread-safe lock for concurrent FastAPI requests
_lock = Lock()

# Schema per model:
# {
#   "success": int,
#   "failure": int,
#   "total_latency_ms": float,
#   "last_used": str | None,
#   "errors": [str],          # last 10 error messages
# }
_stats: Dict[str, dict] = defaultdict(
    lambda: {
        "success": 0,
        "failure": 0,
        "total_latency_ms": 0.0,
        "last_used": None,
        "errors": [],
    }
)


def record_success(model_name: str, latency_ms: float) -> None:
    """Record a successful model call."""
    with _lock:
        _stats[model_name]["success"] += 1
        _stats[model_name]["total_latency_ms"] += latency_ms
        _stats[model_name]["last_used"] = datetime.utcnow().isoformat()


def record_failure(model_name: str, error: str) -> None:
    """Record a failed model call."""
    with _lock:
        _stats[model_name]["failure"] += 1
        errors: List[str] = _stats[model_name]["errors"]
        errors.append(error)
        # Keep only the last 10 errors to avoid unbounded growth
        _stats[model_name]["errors"] = errors[-10:]


def get_stats() -> Dict[str, dict]:
    """Return a snapshot of all model statistics."""
    with _lock:
        snapshot = {}
        for model, data in _stats.items():
            total_calls = data["success"] + data["failure"]
            avg_latency = (
                data["total_latency_ms"] / data["success"]
                if data["success"] > 0
                else 0.0
            )
            snapshot[model] = {
                **data,
                "total_calls": total_calls,
                "avg_latency_ms": round(avg_latency, 2),
                "success_rate": (
                    round(data["success"] / total_calls * 100, 1)
                    if total_calls > 0
                    else 0.0
                ),
            }
        return snapshot


def reset_stats() -> None:
    """Clear all statistics (useful for testing)."""
    with _lock:
        _stats.clear()