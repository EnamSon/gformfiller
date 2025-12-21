import os
import shutil
import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from .db_logger import ActionLogger
from .constants import *

logger = logging.getLogger(__name__)

class FolderManager:
    def __init__(self, root_path = Path.home() / ROOT_DIR):
        self.root = root_path

        # Directories
        self.users_dir = self.root / USERS_DIR
        self.profiles_dir = self.root / PROFILES_DIR

        # Global files
        self.global_log_db = self.root / GLOBAL_LOG_DB
        self.users_db = self.root / USERS_DB
        self.default_config = self.root / DEFAULT_CONFIG

        # Ensure system dirs
        self._ensure_system_dirs()

    def _ensure_system_dirs(self):
        """Create core application directories."""
        for d in [self.users_dir, self.profiles_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def get_user_paths(self, user_id: str) -> dict[str, Path]:
        """Get the root directory for a specific user."""
        base = self.users_dir / user_id
        base.mkdir(parents=True, exist_ok=True)
        return {
            "root": base,
            LOG_DB: base / LOG_DB,
            NOTIFICATIONS_DB: base / NOTIFICATIONS_DB,
            FILLERS_SUBDIR: base / FILLERS_SUBDIR
        }

    # --- PROFILES ---

    def list_profiles(self) -> List[str]:
        return [p.name for p in self.profiles_dir.iterdir() if p.is_dir()]

    def create_profile(self, profile_name: str):
        (self.profiles_dir / profile_name).mkdir(exist_ok=True)
        # self.db_logger.log("CREATE", "PROFILE", profile_name)

    def delete_profile(self, profile_name: str):
        path = self.profiles_dir / profile_name
        if path.exists():
            shutil.rmtree(path)
            # self.db_logger.log("DELETE", "PROFILE", profile_name)

    # --- FILLERS ---

    def list_fillers(self, user_id: str) -> List[str]:
        fillers_dir = self.get_user_paths(user_id)["root"] / FILLERS_SUBDIR
        return [f.name for f in fillers_dir.iterdir() if f.is_dir()]

    def get_filler_paths(self, user_id: str, filler_name: str) -> Dict[str, Path]:
        """Generate dynamic paths for a specific user's filler."""
        users_paths = self.get_user_paths(user_id)
        user_root = users_paths["root"]
        base = user_root / FILLERS_SUBDIR / filler_name
        return {
            "root": base,
            FILES_SUBDIR: base / FILES_SUBDIR,
            RECORD_SUBDIR: base / RECORD_SUBDIR,
            f"{RECORD_SUBDIR}_{PDFS_SUBDIR}": base / RECORD_SUBDIR / PDFS_SUBDIR,
            f"{RECORD_SUBDIR}_{SCREENSHOTS_SUBDIR}": base / RECORD_SUBDIR / SCREENSHOTS_SUBDIR,
            FILLER_LOG_FILE: base / FILLER_LOG_FILE,
            FORMDATA_FILE: base / FORMDATA_FILE,
            CONFIG_FILE: base / CONFIG_FILE,
            METADATA_FILE: base / METADATA_FILE
        }

    def init_filler_structure(self, user_id: str, filler_name: str):
        """Create the complete directory tree for a new filler."""
        paths = self.get_filler_paths(user_id, filler_name)
        for p in paths.values():
            if isinstance(p, Path) and not p.suffix: # Don't create folders for DB files
                p.mkdir(parents=True, exist_ok=True)
        logger.info(f"Structure initialized for filler '{filler_name}' (User: {user_id})")

    def get_log_db(self, user_id) -> Path:
        return self.get_user_paths(user_id)[LOG_DB]

    def get_db_logger(self, user_id) -> ActionLogger:
        log_db = self.get_log_db(user_id)
        return ActionLogger(log_db)

    def _make_db_log(
            self, user_id: str, action: str, category: str, target: str, details: str = ""
    ):
        self.get_db_logger(user_id).log(action, category, target, details)

    def create_filler(self, user_id: str, filler_name: str):
        """Create the complete directory tree for a new filler and init root files."""
        # 1. Create the complete directory tree
        filler_paths = self.get_filler_paths(user_id, filler_name)
        for p in filler_paths.values():
            if isinstance(p, Path) and not p.suffix: # Don't create folders for files
                p.mkdir(parents=True, exist_ok=True)
        logger.info(f"Structure initialized for filler '{filler_name}' (User: {user_id})")

        # 2. Init root files
        self._write_json(filler_paths[FORMDATA_FILE], {})
        self._write_json(filler_paths[CONFIG_FILE], {})
        self._write_json(
            filler_paths[METADATA_FILE],
            {
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            }
        )
        (filler_paths[FILLER_LOG_FILE]).touch()

        # 3. Make logging
        self._make_db_log(user_id, "CREATE", "FILLER", filler_name)

    def delete_filler(self, user_id: str, filler_name: str):
        filler_paths = self.get_filler_paths(user_id, filler_name)
        filler_root = filler_paths["root"]

        if filler_root.exists():
            shutil.rmtree(filler_root)
            self._make_db_log(user_id, "CREATE", "FILLER", filler_name)

    # --- JSON CONTENT (formdata, config, metadata) ---

    def get_filler_file_content(self, user_id: str, filler_name: str, file_key: str) -> Any:
        filler_paths = self.get_filler_paths(user_id, filler_name)
        filler_root = filler_paths["root"]
        filename = self._map_key_to_file(file_key)

        if not filler_root.exists():
            self.create_filler(user_id, filler_name)

        path = filler_root / filename
        return self._read_json(path)

    def update_filler_file_content(
            self, user_id: str, filler_name: str, file_key: str, data: Any, partial: bool = True
    ):
        filename = self._map_key_to_file(file_key)
        filler_paths = self.get_filler_paths(user_id, filler_name)
        fille_root = filler_paths["root"]
        path = fille_root / filename
        
        if partial and path.exists():
            current = self._read_json(path)
            if isinstance(current, dict) and isinstance(data, dict):
                current.update(data)
                data = current
        
        self._write_json(path, data)
        self._make_db_log(user_id, "UPDATE", f"FILLER_{file_key.upper()}", filler_name)

    def delete_filler_file_content(self, user_id: str, filler_name: str, file_key: str):
        filename = self._map_key_to_file(file_key)
        filler_paths = self.get_filler_paths(user_id, filler_name)
        fille_root = filler_paths["root"]
        path = fille_root / filename
        self._write_json(path, {})
        self._make_db_log(user_id, "RESET", f"FILLER_{file_key.upper()}", filler_name)

    # --- FILLER LOGS ---

    def get_filler_log(self, user_id: str, filler_name: str) -> str:
        filler_paths = self.get_filler_paths(user_id, filler_name)
        path = filler_paths[FILLER_LOG_FILE]
        return path.read_text(encoding='utf-8') if path.exists() else ""

    def delete_log(self, user_id: str, filler_name: str):
        filler_paths = self.get_filler_paths(user_id, filler_name)
        path = filler_paths[FILLER_LOG_FILE]
        if path.exists():
            path.write_text("", encoding='utf-8')
            self._make_db_log(user_id, "DELETE", "FILLER_LOG", filler_name)

    # --- FILES (Uploads) ---

    def list_files(self, user_id: str, filler_name: str) -> List[str]:
        filler_paths = self.get_filler_paths(user_id, filler_name)
        path = filler_paths[FILES_SUBDIR]
        return [f.name for f in path.iterdir() if f.is_file()]

    def save_file(self, user_id: str, filler_name: str, filename: str, content: bytes):
        filler_paths = self.get_filler_paths(user_id, filler_name)
        path = filler_paths[FILES_SUBDIR] / filename
        path.write_bytes(content)
        self._make_db_log(user_id, "UPLOAD", "FILE", f"{filler_name}/{filename}")

    def get_file_path(self, user_id, filler_name: str, filename: str) -> Path:
        filler_paths = self.get_filler_paths(user_id, filler_name)
        return filler_paths[FILES_SUBDIR] / filename

    def delete_file(self, user_id: str, filler_name: str, filename: str):
        filler_paths = self.get_filler_paths(user_id, filler_name)
        path = filler_paths[FILES_SUBDIR] / filename
        if path.exists():
            path.unlink()
            self._make_db_log(user_id, "DELETE", "FILE", f"{filler_name}/{filename}")

    # --- RECORDS (PDFs & Screenshots) ---

    def list_records(self, user_id, filler_name: str, record_type: str) -> List[str]:
        sub_dir = PDFS_SUBDIR if record_type == "pdfs" else SCREENSHOTS_SUBDIR
        filler_paths = self.get_filler_paths(user_id, filler_name)
        path = filler_paths[RECORD_SUBDIR] / sub_dir
        return [f.name for f in path.iterdir() if f.is_file()]

    def delete_record(self, user_id: str, filler_name: str, record_type: str, filename: Optional[str] = None):
        sub_dir = PDFS_SUBDIR if record_type == "pdfs" else SCREENSHOTS_SUBDIR
        filler_paths = self.get_filler_paths(user_id, filler_name)
        path = filler_paths[RECORD_SUBDIR] / sub_dir
        
        if filename:
            target = path / filename
            if target.exists(): 
                target.unlink()
                self._make_db_log(user_id, "DELETE", f"RECORD_{record_type.upper()}", f"{filler_name}/{filename}")
        else:
            for f in path.iterdir(): f.unlink()
            self._make_db_log(user_id, "CLEAR", f"RECORDS_{record_type.upper()}", filler_name)

    def get_record_path(
            self, user_id: str, filler_name: str, record_type: str, filename: str
    ) -> Path:
        sub_dir = PDFS_SUBDIR if record_type == "pdfs" else SCREENSHOTS_SUBDIR
        filler_paths = self.get_filler_paths(user_id, filler_name)
        path = filler_paths[RECORD_SUBDIR] / sub_dir
        return filler_paths[RECORD_SUBDIR] / sub_dir / filename

    # --- JSON FILES ---

    def _get_all_filler_files(self, user_id: str, filename: str) -> Dict[str, Any]:
        """
        Generic helper to scan all fillers for a specific JSON file.
        """
        user_paths = self.get_user_paths(user_id)
        fillers_dir = user_paths[FILLERS_SUBDIR]
        all_content = {}
        if not fillers_dir.exists():
            return {}

        for filler_path in fillers_dir.iterdir():
            if filler_path.is_dir():
                filler_name = filler_path.name
                target_file = filler_path / filename

                if target_file.exists():
                    try:
                        with open(target_file, 'r', encoding='utf-8') as f:
                            all_content[filler_name] = json.load(f)
                    except Exception as e:
                        logger.error(f"Error reading {filename} for {filler_name}: {e}")
                        all_content[filler_name] = {"error": str(e)}
        return all_content

    def get_all_metadata(self, user_id: str) -> Dict[str, Any]:
        """Returns metadata for all fillers (URL, status, profile used, etc.)."""
        return self._get_all_filler_files(user_id, METADATA_FILE)

    def get_all_configs(self, user_id) -> Dict[str, Any]:
        """Returns specific configurations for all fillers."""
        return self._get_all_filler_files(user_id, CONFIG_FILE)

    def get_all_form_data(self, user_id) -> Dict[str, Any]:
        """Returns form_data for all fillers"""
        return self._get_all_filler_files(user_id, FORMDATA_FILE)

    # --- UTILS ---

    def _map_key_to_file(self, key: str) -> str:
        mapping = {
            FileKeys.FORMDATA: FORMDATA_FILE,
            FileKeys.CONFIG: CONFIG_FILE,
            FileKeys.METADATA: METADATA_FILE
        }
        return mapping.get(key, f"{key}.json")

    def _read_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists(): return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.error(f"Impossible {str(path)}.")
            return {}

    def _write_json(self, path: Path, data: Any):
        path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding='utf-8')