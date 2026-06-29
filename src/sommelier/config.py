import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str) -> Dict[str, Any]:
    """Load and parse YAML configuration file.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        Dictionary with parsed config

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, 'r') as f:
        config = yaml.safe_load(f)

    if not config:
        raise ValueError("Config file is empty")

    validate_config(config)
    return config


def validate_config(config: Dict[str, Any]) -> None:
    """Validate required keys in config.

    Args:
        config: Configuration dictionary

    Raises:
        ValueError: If required keys are missing
    """
    if 'jobs' not in config:
        raise ValueError("Config must contain 'jobs' key")

    if not isinstance(config['jobs'], list):
        raise ValueError("'jobs' must be a list")

    if not config['jobs']:
        raise ValueError("'jobs' list cannot be empty")

    for i, job in enumerate(config['jobs']):
        if 'template' not in job:
            raise ValueError(f"Job {i} missing 'template' key")
        if 'output' not in job:
            raise ValueError(f"Job {i} missing 'output' key")
        if 'context' not in job:
            raise ValueError(f"Job {i} missing 'context' key")
