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
    def __init__(self, root_path = Path.home() / "gformfiller"):
        self.root = root_path
        self.profiles_dir = self.root / PROFILES_DIR
        self.fillers_dir = self.root / FILLERS_DIR
        self.db_path = self.root / GLOBAL_LOG_DB
        self.default_path = self.root / DEFAULT_TOML
        self._ensure_base_structure()
        self.db_logger = ActionLogger(self.db_path)


    def _ensure_base_structure(self):
        """Initialise l'arborescence de base si nécessaire."""
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.fillers_dir.mkdir(parents=True, exist_ok=True)
        (self.root / CHROME_BIN_DIR).mkdir(exist_ok=True)
        (self.root / CHROMEDRIVER_DIR).mkdir(exist_ok=True)

    # --- PROFILES ---

    def _get_profile_date(self, profile_name) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT timestamp FROM system_logs
            WHERE category == 'PROFILE' and action == 'CREATE' and target == ?""",
            (f"{profile_name}/",)
        )

        res = cursor.fetchone()

        return res[0] if res else datetime.now().isoformat()

    def list_profiles(self) -> List[str]:

        return [p.name for p in self.profiles_dir.iterdir() if p.is_dir()]

    def create_profile(self, profile_name: str):
        (self.profiles_dir / profile_name).mkdir(exist_ok=True)
        self.db_logger.log("CREATE", "PROFILE", profile_name)

    def delete_profile(self, profile_name: str):
        path = self.profiles_dir / profile_name
        if path.exists():
            shutil.rmtree(path)
            self.db_logger.log("DELETE", "PROFILE", profile_name)

    # --- FILLERS ---

    def list_fillers(self) -> List[str]:
        return [f.name for f in self.fillers_dir.iterdir() if f.is_dir()]

    def create_filler(self, filler_name: str):
        f_path = self.fillers_dir / filler_name
        (f_path / RECORD_DIR / PDFS_DIR).mkdir(parents=True, exist_ok=True)
        (f_path / RECORD_DIR / SCREENSHOTS_DIR).mkdir(parents=True, exist_ok=True)
        (f_path / FILES_DIR).mkdir(parents=True, exist_ok=True)
        
        self._write_json(f_path / FORMDATA_FILE, {})
        self._write_json(f_path / CONFIG_FILE, {})
        self._write_json(
            f_path / METADATA_FILE,
            {"created_at": datetime.now().isoformat(), "status": "pending"}
        )
        (f_path / FILLER_LOG_FILE).touch()
        
        self.db_logger.log("CREATE", "FILLER", filler_name)

    def delete_filler(self, filler_name: str):
        path = self.fillers_dir / filler_name
        if path.exists():
            shutil.rmtree(path)
            self.db_logger.log("DELETE", "FILLER", filler_name)

    # --- JSON CONTENT (formdata, config, metadata) ---

    def get_filler_file_content(self, filler_name: str, file_key: str) -> Any:
        filename = self._map_key_to_file(file_key)
        path = self.fillers_dir / filler_name / filename
        return self._read_json(path)

    def update_filler_file_content(self, filler_name: str, file_key: str, data: Any, partial: bool = False):
        filename = self._map_key_to_file(file_key)
        path = self.fillers_dir / filler_name / filename
        
        if partial and path.exists():
            current = self._read_json(path)
            if isinstance(current, dict) and isinstance(data, dict):
                current.update(data)
                data = current
        
        self._write_json(path, data)
        self.db_logger.log("UPDATE", f"FILLER_{file_key.upper()}", filler_name)

    def delete_filler_file_content(self, filler_name: str, file_key: str):
        filename = self._map_key_to_file(file_key)
        path = self.fillers_dir / filler_name / filename
        self._write_json(path, {})
        self.db_logger.log("RESET", f"FILLER_{file_key.upper()}", filler_name)

    # --- FILLER LOGS ---

    def get_log(self, filler_name: str) -> str:
        path = self.fillers_dir / filler_name / FILLER_LOG_FILE
        return path.read_text(encoding='utf-8') if path.exists() else ""

    def delete_log(self, filler_name: str):
        path = self.fillers_dir / filler_name / FILLER_LOG_FILE
        if path.exists():
            path.write_text("", encoding='utf-8')
            self.db_logger.log("DELETE", "FILLER_LOG", filler_name)

    # --- FILES (Uploads) ---

    def list_files(self, filler_name: str) -> List[str]:
        path = self.fillers_dir / filler_name / FILES_DIR
        return [f.name for f in path.iterdir() if f.is_file()]

    def save_file(self, filler_name: str, filename: str, content: bytes):
        path = self.fillers_dir / filler_name / FILES_DIR / filename
        path.write_bytes(content)
        self.db_logger.log("UPLOAD", "FILE", f"{filler_name}/{filename}")

    def get_file_path(self, filler_name: str, filename: str) -> Path:
        return self.fillers_dir / filler_name / FILES_DIR / filename

    def delete_file(self, filler_name: str, filename: str):
        path = self.fillers_dir / filler_name / FILES_DIR / filename
        if path.exists():
            path.unlink()
            self.db_logger.log("DELETE", "FILE", f"{filler_name}/{filename}")

    # --- RECORDS (PDFs & Screenshots) ---

    def list_records(self, filler_name: str, record_type: str) -> List[str]:
        sub_dir = PDFS_DIR if record_type == "pdfs" else SCREENSHOTS_DIR
        path = self.fillers_dir / filler_name / RECORD_DIR / sub_dir
        return [f.name for f in path.iterdir() if f.is_file()]

    def delete_record(self, filler_name: str, record_type: str, filename: Optional[str] = None):
        sub_dir = PDFS_DIR if record_type == "pdfs" else SCREENSHOTS_DIR
        path = self.fillers_dir / filler_name / RECORD_DIR / sub_dir
        
        if filename:
            target = path / filename
            if target.exists(): 
                target.unlink()
                self.db_logger.log("DELETE", f"RECORD_{record_type.upper()}", f"{filler_name}/{filename}")
        else:
            for f in path.iterdir(): f.unlink()
            self.db_logger.log("CLEAR", f"RECORDS_{record_type.upper()}", filler_name)

    def get_record_path(self, filler_name: str, record_type: str, filename: str) -> Path:
        sub_dir = PDFS_DIR if record_type == "pdfs" else SCREENSHOTS_DIR
        return self.fillers_dir / filler_name / RECORD_DIR / sub_dir / filename

    # --- JSON FILES ---

    def _get_all_filler_files(self, filename: str) -> Dict[str, Any]:
        """
        Generic helper to scan all fillers for a specific JSON file.
        """
        all_content = {}
        if not self.fillers_dir.exists():
            return {}

        for filler_path in self.fillers_dir.iterdir():
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

    def get_all_metadata(self) -> Dict[str, Any]:
        """Returns metadata for all fillers (URL, status, profile used, etc.)."""
        return self._get_all_filler_files(METADATA_FILE)

    def get_all_configs(self) -> Dict[str, Any]:
        """Returns specific configurations for all fillers."""
        return self._get_all_filler_files(CONFIG_FILE)

    def get_all_form_data(self) -> Dict[str, Any]:
        """Returns form_data for all fillers"""
        return self._get_all_filler_files(FORMDATA_FILE)

    # --- UTILS ---

    def _map_key_to_file(self, key: str) -> str:
        mapping = {
            "formdata": FORMDATA_FILE,
            "config": CONFIG_FILE,
            "metadata": METADATA_FILE
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