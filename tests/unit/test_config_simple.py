"""
Simplified unit tests for the configuration utilities.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the module directly
from pdf2qa.utils.config import get_default_config, load_config

def test_get_default_config():
    """Test getting the default configuration."""
    config = get_default_config()
    assert "parser" in config
    assert "extractor" in config
    assert "qa_generator" in config
    assert "export" in config


def test_load_config():
    """Test loading configuration from a file."""
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as f:
        config = {
            "parser": {
                "model": "test-model",
                "api_key_env": "TEST_API_KEY",
            },
            "export": {
                "content_path": "./test/content.json",
            },
        }
        yaml.dump(config, f)
        f.flush()
        
        # Load the config
        loaded_config = load_config(f.name)
        
        # Check that the config was loaded correctly
        assert loaded_config["parser"]["model"] == "test-model"
        assert loaded_config["parser"]["api_key_env"] == "TEST_API_KEY"
        assert loaded_config["export"]["content_path"] == "./test/content.json"


def test_load_config_with_env_vars():
    """Test loading configuration with environment variables."""
    # Set environment variable
    os.environ["TEST_API_KEY"] = "test-api-key-value"
    
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as f:
        config = {
            "parser": {
                "model": "test-model",
                "api_key_env": "TEST_API_KEY",
            },
        }
        yaml.dump(config, f)
        f.flush()
        
        # Load the config
        loaded_config = load_config(f.name)
        
        # Check that the environment variable was processed
        assert loaded_config["parser"]["api_key"] == "test-api-key-value"
    
    # Clean up
    del os.environ["TEST_API_KEY"]


def test_load_config_file_not_found():
    """Test loading configuration from a non-existent file."""
    with pytest.raises(FileNotFoundError):
        load_config("non_existent_file.yaml")
