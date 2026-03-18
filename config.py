"""
config.py - Central configuration for the Multi-LLM Smart Router Chatbot.
Loads API keys from environment variables and defines model priorities.
"""

import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# ─── API Keys ────────────────────────────────────────────────────────────────
GROQ_API_KEY         = os.getenv("GROQ_API_KEY", "")
OPENROUTER_API_KEY   = os.getenv("OPENROUTER_API_KEY", "")
MODEL_PRIORITY = ["groq", "openrouter"]

# ─── Model-specific settings ──────────────────────────────────────────────────

GROQ_MODEL          = os.getenv("GROQ_MODEL",         "llama-3.1-8b-instant")
OPENROUTER_MODEL = "openrouter/auto"
# OLLAMA_MODEL        = os.getenv("OLLAMA_MODEL",       "llama3")
# OLLAMA_BASE_URL     = os.getenv("OLLAMA_BASE_URL",    "http://localhost:11434")

# ─── Request timeout (seconds) ───────────────────────────────────────────────
REQUEST_TIMEOUT     = int(os.getenv("REQUEST_TIMEOUT", "20"))

# ─── Router mode ─────────────────────────────────────────────────────────────
# "fallback" → try models in order, return first success
# "best"     → query all models concurrently, pick highest-scored response
ROUTER_MODE = "fallback"

# ─── Model priority list (fallback mode) ─────────────────────────────────────
# Names must match keys registered in router.py MODEL_REGISTRY.
# Ollama is always appended as the final local fallback.

MODEL_PRIORITY = ["deepinfra", "groq", "openrouter"]
