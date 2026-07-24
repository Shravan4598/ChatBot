"""
Centralized logging configuration for the AI Chatbot project.

This module creates a timestamped log file and configures
both file and console logging.
"""

import logging
import os
from datetime import datetime

# -------------------------------------------------------------------
# Create Logs Directory
# -------------------------------------------------------------------

PROJECT_ROOT = os.getcwd()

LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# -------------------------------------------------------------------
# Log File
# -------------------------------------------------------------------

LOG_FILE_NAME = datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".log"

LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE_NAME)

# -------------------------------------------------------------------
# Logger Configuration
# -------------------------------------------------------------------

LOGGER_NAME = "AIChatBot"

logger = logging.getLogger(LOGGER_NAME)

if not logger.handlers:

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] "
        "[%(filename)s:%(lineno)d] - %(message)s"
    )

    # ---------------- File Handler ----------------

    file_handler = logging.FileHandler(
        LOG_FILE_PATH,
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)

    # ---------------- Console Handler ----------------

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)

    # ---------------- Add Handlers ----------------

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.propagate = False