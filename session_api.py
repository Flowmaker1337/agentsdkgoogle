#!/usr/bin/env python3
"""
FastAPI endpoints dla zarządzania sesjami chatu
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
from session_database import SessionDatabase
import asyncio
from contextlib import asynccontextmanager

# Pydantic modele
class CreateSessionRequest(BaseModel):
    title: Optional[str] = "Nowa Rozmowa"
    user_id: Optional[str] = "default_user"

class AddMessageRequest(BaseModel):
    role: str  # 'user' lub 'assistant'
    content: str
    metadata: Optional[Dict] = {}

class UpdateSessionRequest(BaseModel):
    title: str

# Globalna instancja bazy danych
db = SessionDatabase()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.init_database()
    print("🚀 Session API uruchomione")
    yield
    # Shutdown
    print("🛑 Session API zatrzymane")

# FastAPI app
app = FastAPI(
    title="Chat Session API",
    description="API do zarządzania sesjami chatu z historią",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware (dla development)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # W produkcji użyj konkretnych domen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📋 **SESSION ENDPOINTS**

@app.get("/api/sessions")
async def get_sessions(user_id: str = "default_user", limit: int = 50):
    """Pobiera listę sesji dla użytkownika"""
    try:
        sessions = await db.get_sessions(user_id, limit)
        return {
            "success": True,
            "sessions": sessions,
            "count": len(sessions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions")
async def create_session(request: CreateSessionRequest):
    """Tworzy nową sesję"""
    try:
        session_id = await db.create_session(request.title, request.user_id)
        return {
            "success": True,
            "session_id": session_id,
            "title": request.title
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Pobiera szczegóły sesji"""
    try:
        messages = await db.get_session_messages(session_id)
        return {
            "success": True,
            "session_id": session_id,
            "messages": messages,
            "message_count": len(messages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/sessions/{session_id}")
async def update_session(session_id: str, request: UpdateSessionRequest):
    """Aktualizuje sesję (np. tytuł)"""
    try:
        await db.update_session_title(session_id, request.title)
        return {
            "success": True,
            "session_id": session_id,
            "title": request.title
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Usuwa sesję"""
    try:
        await db.delete_session(session_id)
        return {
            "success": True,
            "message": "Sesja została usunięta"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 💬 **MESSAGE ENDPOINTS**

@app.get("/api/sessions/{session_id}/messages")
async def get_messages(session_id: str):
    """Pobiera wiadomości z sesji"""
    try:
        messages = await db.get_session_messages(session_id)
        return {
            "success": True,
            "session_id": session_id,
            "messages": messages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions/{session_id}/messages")
async def add_message(session_id: str, request: AddMessageRequest):
    """Dodaje wiadomość do sesji"""
    try:
        message_id = await db.add_message(
            session_id, 
            request.role, 
            request.content, 
            request.metadata
        )
        return {
            "success": True,
            "message_id": message_id,
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🎯 **UTILITY ENDPOINTS**

@app.post("/api/sessions/{session_id}/generate-title")
async def generate_session_title(session_id: str):
    """Generuje tytuł sesji na podstawie treści"""
    try:
        title = await db.generate_session_title(session_id)
        await db.update_session_title(session_id, title)
        return {
            "success": True,
            "session_id": session_id,
            "title": title
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Chat Session API",
        "version": "1.0.0"
    }

# 📁 **STATIC FILES** (dla Glass UI)
# Serwowanie plików statycznych
try:
    app.mount("/static", StaticFiles(directory="."), name="static")
except Exception:
    pass  # Directory może nie istnieć w testach

@app.get("/")
async def serve_ui():
    """Serwuje Glass UI"""
    try:
        return FileResponse("modern_glass_agent_ui.html")
    except Exception:
        return {"message": "Glass UI not found. Place modern_glass_agent_ui.html in the same directory."}

# 🔧 **DEVELOPMENT SERVER**
if __name__ == "__main__":
    print("🚀 Uruchamianie Session API...")
    print("📖 Dokumentacja API: http://localhost:8000/docs")
    print("🎨 Glass UI: http://localhost:8000/")
    
    uvicorn.run(
        "session_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload podczas development
        log_level="info"
    ) 