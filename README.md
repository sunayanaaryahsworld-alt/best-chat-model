# Multi-LLM Smart Router Chatbot

A production-grade FastAPI service that routes prompts through **9 LLM providers** with automatic failover and a local Ollama safety net.

---

## Features

| Feature | Details |
|---|---|
| **Providers** | Gemini, Groq, OpenRouter, Together AI, Cohere, HuggingFace, Replicate, Fireworks, Ollama |
| **Fallback mode** | Try models in priority order → return first success |
| **Best-model mode** | Query all models concurrently → return highest-scored response |
| **Error handling** | Timeout, quota, auth, network, empty-response errors all handled gracefully |
| **Usage tracking** | Per-model success/failure counts, latency, success rate |
| **Response scoring** | Length, lexical diversity, refusal detection |

---

## Project Structure

```
project/
├── main.py              # FastAPI app + endpoints
├── router.py            # Core routing logic (fallback & best-model modes)
├── config.py            # All settings loaded from environment variables
├── usage_tracker.py     # In-memory per-model stats
├── evaluator.py         # Response scoring for best-model mode
├── models/
│   ├── gemini_model.py
│   ├── groq_model.py
│   ├── openrouter_model.py
│   ├── together_model.py
│   ├── cohere_model.py
│   ├── huggingface_model.py
│   ├── replicate_model.py
│   ├── fireworks_model.py
│   └── ollama_model.py
├── requirements.txt
└── .env.example
```

---

## Quick Start

### 1. Clone / copy the project

```bash
cd project
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API keys

```bash
cp .env.example .env
# Open .env in your editor and add your real API keys
```

You only need keys for the providers you want to use.  
Models without a key are automatically skipped.

### 5. (Optional) Install and start Ollama for local fallback

```bash
# Install: https://ollama.com/download
ollama pull llama3        # or whichever model you set in OLLAMA_MODEL
ollama serve              # starts on http://localhost:11434
```

### 6. Run the server

```bash
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## API Endpoints

### Chat

```
GET /chat?q=<your prompt>
```

**Example:**
```bash
curl "http://localhost:8000/chat?q=Explain+quantum+entanglement+simply"
```

**Response:**
```json
{
  "response": "Quantum entanglement is...",
  "model_used": "groq",
  "mode": "fallback",
  "tried": ["gemini", "groq"],
  "failed": ["gemini"]
}
```

### Usage Statistics

```
GET /stats
```

Returns per-model success/failure counts, average latency, and recent errors.

### Reset Statistics

```
POST /stats/reset
```

### Health Check

```
GET /health
```

---

## Configuration Reference

All settings live in `.env` (copied from `.env.example`):

| Variable | Default | Description |
|---|---|---|
| `ROUTER_MODE` | `fallback` | `fallback` or `best` |
| `MODEL_PRIORITY` | all models | Comma-separated priority order |
| `REQUEST_TIMEOUT` | `20` | Seconds per API call |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3` | Model to use in Ollama |
| `*_MODEL` | see config.py | Model name per provider |

---

## Router Modes

### Fallback Mode (`ROUTER_MODE=fallback`)

```
Prompt → Gemini → [fail] → Groq → [success] → Response
```

Models are tried in `MODEL_PRIORITY` order. The first successful response wins. Ollama is always appended as the last resort.

### Best-Model Mode (`ROUTER_MODE=best`)

```
Prompt → [Gemini, Groq, OpenRouter, ...] (concurrent)
       → Score all responses
       → Return highest-scored response
```

All models are queried simultaneously. The evaluator scores each response on length, lexical diversity, and absence of refusal phrases.

---

## Adding a New Provider

1. Create `models/my_provider_model.py` with a single function:
   ```python
   def ask_model(prompt: str) -> str:
       ...
   ```
2. Add the name → module mapping in `router.py` → `_load_model()`.
3. Add the key/model name to `config.py` and `.env.example`.
4. Add the name to `MODEL_PRIORITY` in your `.env`.

---

## License

MIT
