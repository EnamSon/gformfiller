# gformfiller/infrastructure/folder_manager/db_logger.py

import sqlite3
from datetime import datetime
from pathlib import Path

class ActionLogger:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    action TEXT,
                    category TEXT,
                    target TEXT,
                    details TEXT
                )
            """)
            conn.commit()

    def log(self, action: str, category: str, target: str, details: str = ""):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO system_logs (timestamp, action, category, target, details) VALUES (?, ?, ?, ?, ?)",
                (datetime.now().isoformat(), action, category, target, details)
            )
            conn.commit()

    def get_logs(self, limit: int = 100):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, timestamp, action, category, target, details FROM system_logs ORDER BY id DESC LIMIT ?", 
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]