Best-Chat-Model

Multi-model chatbot using FastAPI + OpenRouter + Groq + Router + Evaluator + Firebase tracking.
The system sends query to multiple models and returns the best response.

Project Structure
Best-Chat-Model/

backend/
│
├── app/
│   ├── api/
│   ├── config/
│   ├── prompts/
│   ├── services/
│   ├── utils/
│
├── router/
│   ├── models/
│
embeddings/
frontend/
knowledge_base/
venv/

main.py
router.py
evaluator.py
usage_tracker.py
requirements.txt
.env
firebase_key.json
chatbot_ui.html
test_models.py
test_router.py
Folder Description
backend/

Backend logic of chatbot.

app/api → API routes
app/config → config settings
app/prompts → prompt templates
app/services → API calls
app/utils → helper functions
router/models → model handlers
frontend/

UI files.

chatbot_ui.html → chat UI
JS / CSS inside frontend
embeddings/

Stores embeddings (if used).

knowledge_base/

Static answers / FAQ.

router.py

Routes request to models.

evaluator.py

Selects best response.

usage_tracker.py

Logs usage in Firebase.

main.py

FastAPI entry point.

Runs backend.

.env
GROQ_API_KEY=
OPENROUTER_API_KEY=
firebase_key.json

Firebase credentials.

Required for usage tracking.

requirements.txt

Python libraries.

Setup Steps
Step 1 — Open project folder
F:\Best-Chat-Model

Add Firebase file:

firebase_key.json

Activate venv:

venv\Scripts\activate

You should see:

(venv) PS F:\Best-Chat-Model>
Step 2 — Install requirements
pip install -r requirements.txt

Only first time.

Step 3 — Check .env
GROQ_API_KEY=xxxx
OPENROUTER_API_KEY=xxxx

If missing → API fails.

Step 4 — Run backend

Run:

uvicorn main:app --reload

Output:

Uvicorn running on http://127.0.0.1:8000

Backend running.

Step 5 — Test API

Open:

http://127.0.0.1:8000/health

Expected:

{"status":"ok"}

Test chat:

http://127.0.0.1:8000/chat?q=hello

Router working.

Step 6 — Open UI

Open file:

frontend/chatbot_ui.html

Open in browser.

UI connects to:

http://127.0.0.1:8000
Step 7 — Test chat

Type:

Explain AI

Console:

Trying openrouter...
Trying groq...

Response appears.

Project running.

Test Files
test_models.py
python test_models.py

Tests APIs only.

test_router.py
python test_router.py

Tests router only.

Correct Order

1 Activate venv
2 Run backend
3 Open UI
4 Send message

venv\Scripts\activate
uvicorn main:app --reload
open chatbot_ui.html

Done.

Project Flow
chatbot_ui.html
    ↓
main.py (FastAPI)
    ↓
router.py
    ↓
models/*
    ↓
evaluator.py
    ↓
usage_tracker.py
    ↓
Response
Features
OpenRouter + Groq
Best model selection
Router system
FastAPI backend
HTML UI
Firebase logging
Env config
Multi-model support