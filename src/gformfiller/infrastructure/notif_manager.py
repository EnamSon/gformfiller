# /gformfiller/infrastructure/notif_manager.py

import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from gformfiller.infrastructure.folder_manager import FolderManager
from gformfiller.infrastructure.folder_manager.constants import (
    NOTIFICATIONS_DB
)

class NotifManager:
    def __init__(self, fm: FolderManager):
        self.fm = fm

    def _get_notif_db(self, user_id):
        user_paths = self.fm.get_user_paths(user_id)
        notif_db = user_paths[NOTIFICATIONS_DB]
        with sqlite3.connect(notif_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filler_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        return notif_db

    def add_notification(self, user_id: str, filler_name: str, status: str):
        notif_db = self._get_notif_db(user_id)
        with sqlite3.connect(notif_db) as conn:
            cursor = conn.execute(
                "INSERT INTO notifications (filler_name, status) VALUES (?, ?)",
                (filler_name, status)
            )
            return cursor.lastrowid

    def get_notifications(self, user_id, last_id: int = 0) -> List[Dict[str, Any]]:
        notif_db = self._get_notif_db(user_id)
        with sqlite3.connect(notif_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id, filler_name, status, created_at FROM notifications WHERE id >= ? ORDER BY id ASC",
                (last_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_notif_by_id(self, user_id: str, notif_id: int):
        notif_db = self._get_notif_db(user_id)
        with sqlite3.connect(notif_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM notifications WHERE id = ?", (notif_id,))
            row = cursor.fetchone()
            return dict(row) if row else None