from fastapi import APIRouter
import requests

router = APIRouter()

@router.get("/debug/groq")
def debug_groq():
    try:
        r = requests.get("https://api.groq.com", timeout=5)
        return {"status": "reachable", "code": r.status_code}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
