# tests/unit/infrastructure/test_config_manager.py

import pytest
from gformfiller.infrastructure.folder_manager import FolderManager
from gformfiller.infrastructure.config_manager import ConfigManager

@pytest.fixture
def config_setup(tmp_path):
    fm = FolderManager()
    
    # Création d'un default.toml de test
    default_toml = tmp_path / "default.toml"
    default_toml.write_text("""
[default]
profile = "global_profile"
wait_time = 10.0
model_type = "OPENAI"
""", encoding="utf-8")
    
    return fm, ConfigManager(fm)

def test_resolved_config_merge(config_setup):
    fm, cm = config_setup
    fm.create_filler("test_merge")
    
    # Override local
    fm.update_filler_file_content("test_merge", "config", {"wait_time": 5.0, "profile": "global_profile"})
    
    resolved = cm.get_resolved_config("test_merge")
    
    # Doit prendre le profile du global et le wait_time du local
    assert resolved.profile == "global_profile"
    assert resolved.wait_time == 5.0
    assert resolved.model_type == "OPENAI"

def test_invalid_config_raises_error(config_setup):
    fm, cm = config_setup
    fm.create_filler("test_error")
    
    # wait_time doit être un float/int, pas une string
    fm.update_filler_file_content("test_error", "config", {"wait_time": "beaucoup"})
    
    with pytest.raises(Exception): # Pydantic ValidationError
        cm.get_resolved_config("test_error")