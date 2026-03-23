import os
from router.router import route
from app.prompts.system_prompt import SYSTEM_PROMPT

def generate_ai_reply(message: str, history=None) -> str:
    try:

        prompt = f"""
{SYSTEM_PROMPT}

User: {message}
"""

        result = route(prompt)

        reply = result["response"]

        # ✅ clean formatting
        reply = reply.replace("**", "")
        reply = reply.replace("*", "")
        reply = reply.replace("##", "")
        reply = reply.replace("###", "")
        reply = reply.replace("- ", "• ")
        
        return reply

    except Exception as e:
        print("❌ ROUTER ERROR:", repr(e))
        return "Sorry, AI temporarily unavailable."