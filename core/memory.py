import aiosqlite
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "memory.db")

class AsyncMemoryDB:
    @staticmethod
    async def init_db():
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    @staticmethod
    async def add_message(chat_id, role, content):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO history (chat_id, role, content) VALUES (?, ?, ?)",
                (str(chat_id), role, content)
            )
            await db.commit()

    @staticmethod
    async def get_history(chat_id, limit=6):
        """Devuelve los últimos mensajes en orden cronológico (limit = 6 implica 3 interacciones)"""
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT role, content FROM history WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
                (str(chat_id), limit)
            ) as cursor:
                rows = await cursor.fetchall()
                # Revertir para que el orden sea cronológico
                return [{"role": row[0], "content": row[1]} for row in reversed(rows)]
                
    @staticmethod
    async def clear_history(chat_id):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("DELETE FROM history WHERE chat_id = ?", (str(chat_id),))
            await db.commit()
