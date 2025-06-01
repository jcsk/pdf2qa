"""
Configuration utilities for the pdf2qa library.
"""

import os
from pathlib import Path
from typing import Any, Dict, Union

import yaml

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, skip loading .env file
    pass


def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to the configuration file.

    Returns:
        Dictionary containing the configuration.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        ValueError: If the configuration file is not valid YAML.
    """
    config_path = Path(config_path) if isinstance(config_path, str) else config_path

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {e}")

    # Process environment variables in the config
    _process_env_vars(config)

    return config


def _process_env_vars(config: Dict[str, Any]) -> None:
    """
    Process environment variables in the configuration.

    Args:
        config: Configuration dictionary to process.
    """
    for section_config in config.values():
        if not isinstance(section_config, dict):
            continue

        # Create a list of items to add to avoid modifying during iteration
        items_to_add = {}

        for key, value in section_config.items():
            if key.endswith("_env") and isinstance(value, str):
                env_var = os.environ.get(value)
                if env_var:
                    # Create a new key without the _env suffix
                    base_key = key[:-4]  # Remove _env suffix
                    items_to_add[base_key] = env_var

        # Update the section config with the new items
        section_config.update(items_to_add)


def get_default_config() -> Dict[str, Any]:
    """
    Get the default configuration.

    Returns:
        Dictionary containing the default configuration.
    """
    return {
        "parser": {
            "language": "en",
            "api_key_env": "LLAMA_CLOUD_API_KEY",
            "chunk_size": 1500,
            "chunk_overlap": 200,
        },
        "extractor": {
            "openai_model": "gpt-3.5-turbo",
            "schema_path": "./schemas/statement.json",
            "api_key_env": "OPENAI_API_KEY",
        },
        "qa_generator": {
            "openai_model": "gpt-3.5-turbo",
            "temperature": 0.0,
            "max_tokens": 256,
            "batch_size": 5,
            "api_key_env": "OPENAI_API_KEY",
        },
        "export": {
            "content_path": "./output/content.json",
            "qa_jsonl_path": "./output/qa.jsonl",
        },
    }
