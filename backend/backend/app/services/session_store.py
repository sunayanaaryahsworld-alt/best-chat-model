# backend/app/services/session_store.py

from collections import defaultdict

chat_sessions = defaultdict(list)

def add_message(session_id: str, role: str, content: str):
    chat_sessions[session_id].append({
        "role": role,
        "content": content
    })

def get_history(session_id: str):
    return chat_sessions[session_id]
