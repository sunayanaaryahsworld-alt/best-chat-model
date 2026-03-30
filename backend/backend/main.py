from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.debug import router as debug_router
from app.api.chat import router as chat_router
import os

# --------------------------------
# Create FastAPI app
# --------------------------------
app = FastAPI(
    title="Nexsalon GenAI Assistant",
    version="1.0.0"
)

# --------------------------------
# CORS (optional but recommended)
# --------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten later in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------
# Routers
# --------------------------------
app.include_router(chat_router)
app.include_router(debug_router)

# --------------------------------
# Health check (optional)
# --------------------------------
@app.get("/")
def health():
    return {"status": "ok"}
