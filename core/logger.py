  # core/logger.py
"""
Central logging setup for the AI ChatBot project.
Creates a timestamped file logger in logs/ and a console handler.
Idempotent: re-importing this module won't add duplicate handlers.
"""

import logging
import os
from datetime import datetime
from pathlib import Path

# Default log directory
LOG_ROOT = Path(os.getenv("LOG_ROOT", "logs"))
LOG_ROOT.mkdir(parents=True, exist_ok=True)

# Create a time-stamped log filename
timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
LOG_FILENAME = f"chatbot_{timestamp}.log"
LOG_PATH = LOG_ROOT / LOG_FILENAME

# Logger instance
logger = logging.getLogger("AIChatBot")
logger.setLevel(logging.INFO)

# Formatting
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# Avoid adding duplicate handlers if module is reloaded
if not logger.handlers:
    # File handler
    try:
        fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception:
        # If file handler cannot be created (permissions, readonly FS), continue with console only
        pass

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Public API: logger
__all__ = ["logger"]