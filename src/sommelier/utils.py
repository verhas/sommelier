import os
from pathlib import Path
from shutil import copy2
import logging

logger = logging.getLogger(__name__)


def ensure_directories(path: str) -> Path:
    """Create directories recursively if they don't exist.

    Args:
        path: Directory path to create

    Returns:
        Path object for the created directory
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured directory exists: {p}")
    return p


def safe_write_file(path: str, content: str) -> None:
    """Write content to file with backup of existing file.

    Args:
        path: File path to write to
        content: Content to write
    """
    p = Path(path)
    ensure_directories(p.parent)

    if p.exists():
        backup_path = Path(str(p) + '.bak')
        copy2(p, backup_path)
        logger.info(f"Backed up existing file to {backup_path}")

    with open(p, 'w') as f:
        f.write(content)
    logger.debug(f"Wrote file: {p}")


def get_example_templates_path() -> Path:
    """Get path to bundled example templates.

    Returns:
        Path to examples directory
    """
    return Path(__file__).parent.parent.parent / "examples"


def get_package_root() -> Path:
    """Get the root directory of the sommelier package.

    Returns:
        Path to package root
    """
    return Path(__file__).parent.parent.parent
