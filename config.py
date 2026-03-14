"""
config.py - Central configuration for the Multi-LLM Smart Router Chatbot.
Loads API keys from environment variables and defines model priorities.
"""

import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# ─── API Keys ────────────────────────────────────────────────────────────────
GEMINI_API_KEY       = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY         = os.getenv("GROQ_API_KEY", "")
OPENROUTER_API_KEY   = os.getenv("OPENROUTER_API_KEY", "")
TOGETHER_API_KEY     = os.getenv("TOGETHER_API_KEY", "")
COHERE_API_KEY       = os.getenv("COHERE_API_KEY", "")
REPLICATE_API_KEY    = os.getenv("REPLICATE_API_KEY", "")
FIREWORKS_API_KEY    = os.getenv("FIREWORKS_API_KEY", "")

# ─── Model-specific settings ──────────────────────────────────────────────────
GEMINI_MODEL        = os.getenv("GEMINI_MODEL",        "models/gemini-1.5-flash")
GROQ_MODEL          = os.getenv("GROQ_MODEL",         "llama-3.1-8b-instant")
OPENROUTER_MODEL    = os.getenv("OPENROUTER_MODEL",   "mistralai/mistral-7b-instruct")
TOGETHER_MODEL      = os.getenv("TOGETHER_MODEL",     "mistralai/Mistral-7B-Instruct-v0.1")
COHERE_MODEL        = os.getenv("COHERE_MODEL",        "command-r-plus")
REPLICATE_MODEL     = os.getenv("REPLICATE_MODEL",    "meta/meta-llama-3-8b-instruct")
FIREWORKS_MODEL     = os.getenv("FIREWORKS_MODEL",    "accounts/fireworks/models/llama-v3-8b-instruct")
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
MODEL_PRIORITY = [
    name.strip()
    for name in os.getenv(
        "MODEL_PRIORITY",
        "gemini,groq,openrouter",
    ).split(",")
    if name.strip()
]
