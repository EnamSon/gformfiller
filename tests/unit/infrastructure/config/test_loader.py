# tests/unit/infrastructure/config/test_loader.py

from gformfiller.infrastructure.config import ConfigInitializer, ConfigLoader

class TestConfigLoader:
    """Tests for ConfigLoader"""
    
    def test_load_from_env(self, clean_env, temp_config_dir, monkeypatch):
        """Test loading configuration from environment variables"""
        # clean_env FIRST to ensure clean state
        ConfigInitializer.initialize()
        
        monkeypatch.setenv("GFORMFILLER_TIMEOUTS_PAGE_LOAD", "90")
        monkeypatch.setenv("GFORMFILLER_AI_DEFAULT_PROVIDER", "openai")
        
        config = ConfigLoader.load()
        
        assert config.timeouts.page_load == 90
        assert config.ai.default_provider == "openai"
    
    def test_priority_env_over_file(self, clean_env, temp_config_dir, write_config_file, 
                                    sample_config_dict, monkeypatch):
        """Test environment variables take priority over file"""
        # clean_env FIRST
        sample_config_dict["timeouts"]["page_load"] = 30
        write_config_file(sample_config_dict)
        
        monkeypatch.setenv("GFORMFILLER_TIMEOUTS_PAGE_LOAD", "60")
        
        config = ConfigLoader.load()
        
        assert config.timeouts.page_load == 60  # ENV wins
    
    def test_load_preserves_unmodified_values(self, clean_env, temp_config_dir, monkeypatch):
        """Test that only overridden values change, others remain default"""
        # clean_env FIRST
        ConfigInitializer.initialize()
        
        monkeypatch.setenv("GFORMFILLER_TIMEOUTS_PAGE_LOAD", "60")
        
        config = ConfigLoader.load()
        
        # Modified value
        assert config.timeouts.page_load == 60
        
        # Unmodified values should be default
        assert config.timeouts.element_wait == 10
        assert config.timeouts.ai_response == 60
        assert config.ai.temperature == 0.7


class TestConfigLoaderParsing:
    """Tests for ConfigLoader parsing methods"""
    
    # ... (autres tests inchangés)
    
    def test_load_from_env_nested_keys(self, clean_env, temp_config_dir, monkeypatch):
        """Test loading nested configuration from environment"""
        # clean_env FIRST
        ConfigInitializer.initialize()
        
        monkeypatch.setenv("GFORMFILLER_TIMEOUTS_PAGE_LOAD", "60")
        monkeypatch.setenv("GFORMFILLER_TIMEOUTS_ELEMENT_WAIT", "20")
        monkeypatch.setenv("GFORMFILLER_AI_TEMPERATURE", "0.5")
        
        env_config = ConfigLoader._load_from_env()
        
        assert "timeouts" in env_config
        assert "page_load" in env_config["timeouts"]
        assert env_config["timeouts"]["page_load"] == 60
        assert env_config["timeouts"]["element_wait"] == 20
        assert env_config["ai"]["temperature"] == 0.5