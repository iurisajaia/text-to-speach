"""Utility functions for the TTS project."""

import logging
import tempfile
from pathlib import Path
from typing import Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def log_info(message: str) -> None:
    """Log an info message."""
    logger.info(message)


def log_warning(message: str) -> None:
    """Log a warning message."""
    logger.warning(message)


def log_error(message: str) -> None:
    """Log an error message."""
    logger.error(message)


def make_temp_directory(prefix: str = "tts_chunks_") -> Path:
    """Create a temporary directory and return its path."""
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    return Path(temp_dir)


def ensure_directory_exists(path: Path) -> None:
    """Ensure the parent directory of the given path exists."""
    path.parent.mkdir(parents=True, exist_ok=True)


