# gformfiller/infrastructure/auth_manager.py

import sqlite3
import secrets
import logging
from pathlib import Path
from passlib.context import CryptContext
from gformfiller.infrastructure.folder_manager import FolderManager

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthManager:
    def __init__(self, fm: FolderManager):
        self.db_path = fm.users_db
        self._init_db()

    def _init_db(self):
        """Initialize global users database with English logs."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        hashed_password TEXT NOT NULL,
                        api_key TEXT UNIQUE NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            logger.info(f"Auth database initialized at: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize auth database: {e}")

    def create_user(self, username, password):
        """Hash password, generate API key and save user."""
        hashed = pwd_context.hash(password)
        api_key = secrets.token_urlsafe(32)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO users (username, hashed_password, api_key) VALUES (?, ?, ?)",
                    (username, hashed, api_key)
                )
            logger.info(f"New user created: '{username}'")
            return api_key
        except sqlite3.IntegrityError:
            logger.warning(f"Signup conflict: Username '{username}' already exists.")
            return None

    def verify_user(self, username, password):
        """Check credentials and return API key if valid."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            
        if user and pwd_context.verify(password, user["hashed_password"]):
            logger.info(f"Successful login for user: '{username}'")
            return user["api_key"]
            
        logger.warning(f"Failed login attempt for user: '{username}'")
        return None

    def get_user_by_token(self, token: str):
        """Retrieve username associated with an API key."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute("SELECT username FROM users WHERE api_key = ?", (token,)).fetchone()