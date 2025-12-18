# tests/unit/infrastructure/test_folder_manager.py

import pytest
import sqlite3
from gformfiller.infrastructure.folder_manager import FolderManager
from gformfiller.infrastructure.folder_manager.constants import GLOBAL_LOG_DB

@pytest.fixture
def fm(tmp_path):
    """Initialise un FolderManager dans un dossier temporaire."""
    return FolderManager(tmp_path)

def test_base_structure_creation(fm, tmp_path):
    assert (tmp_path / "profiles").exists()
    assert (tmp_path / "fillers").exists()
    assert (tmp_path / GLOBAL_LOG_DB).exists()

def test_profile_lifecycle(fm):
    fm.create_profile("test_user")
    assert "test_user" in fm.list_profiles()
    
    fm.delete_profile("test_user")
    assert "test_user" not in fm.list_profiles()

def test_filler_creation_and_db_log(fm):
    fm.create_filler("test_filler")
    
    with sqlite3.connect(fm.db_path) as conn:
        res = conn.execute("SELECT count(*) FROM system_logs").fetchone()
        assert res[0] > 0

def test_json_content_update(fm):
    fm.create_filler("test_json")
    data = {"key": "value"}
    fm.update_filler_file_content("test_json", "config", data)
    
    content = fm.get_filler_file_content("test_json", "config")
    assert content["key"] == "value"