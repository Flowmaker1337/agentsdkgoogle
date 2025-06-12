#!/usr/bin/env python3
"""
System zarządzania sesjami dla Glass UI Chat
Używa SQLite do persistencji historii rozmów
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
import asyncio
import aiosqlite
from pathlib import Path

class SessionDatabase:
    def __init__(self, db_path: str = "chat_sessions.db"):
        self.db_path = db_path
        
    async def init_database(self):
        """Inicjalizuje bazę danych z tabelami"""
        async with aiosqlite.connect(self.db_path) as db:
            # Tabela sesji
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT DEFAULT 'default_user',
                    agent_name TEXT DEFAULT 'GoogleADKBusinessAgent',
                    metadata TEXT DEFAULT '{}'
                )
            """)
            
            # Tabela wiadomości
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)
            
            # Indeksy dla wydajności
            await db.execute("CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_sessions_updated_at ON sessions(updated_at DESC)")
            
            await db.commit()
            print("✅ Baza danych zainicjowana")

    async def create_session(self, title: str = "Nowa Rozmowa", user_id: str = "default_user") -> str:
        """Tworzy nową sesję"""
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO sessions (id, title, created_at, updated_at, user_id)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, title, now, now, user_id))
            await db.commit()
            
        print(f"✅ Utworzono sesję: {session_id} - '{title}'")
        return session_id

    async def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None) -> str:
        """Dodaje wiadomość do sesji"""
        message_id = str(uuid.uuid4())
        metadata_json = json.dumps(metadata or {})
        now = datetime.now().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            # Dodaj wiadomość
            await db.execute("""
                INSERT INTO messages (id, session_id, role, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (message_id, session_id, role, content, now, metadata_json))
            
            # Aktualizuj czas ostatniej aktywności sesji
            await db.execute("""
                UPDATE sessions SET updated_at = ? WHERE id = ?
            """, (now, session_id))
            
            await db.commit()
            
        print(f"✅ Dodano wiadomość do sesji {session_id}: {role}")
        return message_id

    async def get_sessions(self, user_id: str = "default_user", limit: int = 50) -> List[Dict]:
        """Pobiera listę sesji dla użytkownika"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT id, title, created_at, updated_at, 
                       (SELECT COUNT(*) FROM messages WHERE session_id = sessions.id) as message_count
                FROM sessions 
                WHERE user_id = ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_session_messages(self, session_id: str) -> List[Dict]:
        """Pobiera wszystkie wiadomości z sesji"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT id, role, content, timestamp, metadata
                FROM messages 
                WHERE session_id = ?
                ORDER BY timestamp ASC
            """, (session_id,))
            
            rows = await cursor.fetchall()
            messages = []
            for row in rows:
                msg = dict(row)
                msg['metadata'] = json.loads(msg['metadata'])
                messages.append(msg)
            return messages

    async def update_session_title(self, session_id: str, title: str):
        """Aktualizuje tytuł sesji"""
        now = datetime.now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?
            """, (title, now, session_id))
            await db.commit()

    async def delete_session(self, session_id: str):
        """Usuwa sesję i wszystkie jej wiadomości"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            await db.commit()
        print(f"✅ Usunięto sesję: {session_id}")

    async def generate_session_title(self, session_id: str) -> str:
        """Generuje tytuł sesji na podstawie pierwszych wiadomości"""
        messages = await self.get_session_messages(session_id)
        
        if not messages:
            return "Pusta rozmowa"
            
        # Znajdź pierwszą wiadomość użytkownika
        user_message = next((msg for msg in messages if msg['role'] == 'user'), None)
        
        if user_message:
            # Skróć do max 50 znaków
            content = user_message['content'][:50]
            if len(user_message['content']) > 50:
                content += "..."
            return content
        
        return f"Rozmowa z {datetime.now().strftime('%d.%m.%Y')}"

# Test funkcji
async def test_database():
    """Test funkcjonalności bazy danych"""
    db = SessionDatabase()
    await db.init_database()
    
    # Test tworzenia sesji
    session_id = await db.create_session("Test Chat")
    
    # Test dodawania wiadomości
    await db.add_message(session_id, "user", "Cześć! Jak się masz?")
    await db.add_message(session_id, "assistant", "Cześć! Mam się świetnie, dziękuję za pytanie!")
    
    # Test pobierania sesji
    sessions = await db.get_sessions()
    print("📋 Sesje:", sessions)
    
    # Test pobierania wiadomości
    messages = await db.get_session_messages(session_id)
    print("💬 Wiadomości:", messages)
    
    # Test generowania tytułu
    title = await db.generate_session_title(session_id)
    await db.update_session_title(session_id, title)
    print(f"📝 Wygenerowany tytuł: {title}")

if __name__ == "__main__":
    asyncio.run(test_database()) 