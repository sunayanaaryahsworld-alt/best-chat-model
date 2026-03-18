✅ Step 1 — Open project folder in terminal

Go to project folder:

F:\Best-Chat-Model

Activate venv:

venv\Scripts\activate

You should see:

(venv) PS F:\Best-Chat-Model>

✅ Correct

✅ Step 2 — Install requirements (only first time)

Run:

pip install -r requirements.txt

Only needed once.

✅ Step 3 — Check .env file

Make sure .env has keys:

GROQ_API_KEY=xxxx
OPENROUTER_API_KEY=xxxx
DEEPINFRA_API_KEY=xxxx

If missing → APIs fail.

✅ Step 4 — Run backend (IMPORTANT)

You must run FastAPI first.

Run:

uvicorn main:app --reload

You should see:

Uvicorn running on http://127.0.0.1:8000

✅ Backend running

✅ Step 5 — Test API (optional)

Open browser:

http://127.0.0.1:8000/health

Should show:

{"status":"ok"}

Test chat:

http://127.0.0.1:8000/chat?q=hello

✅ Router works

✅ Step 6 — Open UI

Go to:

frontend/chatbot_ui.html

Open in browser.

OR right click → Open with browser

Now UI connects to:

http://127.0.0.1:8000
✅ Step 7 — Test chat

Type:

Explain AI

You should see:

Trying openrouter...
Trying groq...

And response.

✅ Project running

✅ When to run test files
test_models.py

Used to test APIs only

python test_models.py

Not required for UI.

test_router.py

Used to test router only

python test_router.py

Not required for UI.

✅ Correct order to run project
1. Activate venv
2. python main.py
3. open chatbot_ui.html
4. send message

That’s it.

✅ Project flow (important)
chatbot_ui.html
    ↓
main.py (FastAPI)
    ↓
router.py
    ↓
models/*
    ↓
evaluator.py (if best mode)
    ↓
usage_tracker.py