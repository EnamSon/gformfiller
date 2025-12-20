# /gformfiller/infrastructure/notif_manager.py

import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from gformfiller.infrastructure.folder_manager import FolderManager


class NotifManager:
    def __init__(self, fm: FolderManager):
        self.db_path = fm.root / "notifications.db"
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filler_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def add_notification(self, filler_name: str, status: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO notifications (filler_name, status) VALUES (?, ?)",
                (filler_name, status)
            )
            return cursor.lastrowid

    def get_notifications(self, last_id: int = 0) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id, filler_name, status, created_at FROM notifications WHERE id >= ? ORDER BY id ASC",
                (last_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_notif_by_id(self, notif_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM notifications WHERE id = ?", (notif_id,))
            row = cursor.fetchone()
            return dict(row) if row else None