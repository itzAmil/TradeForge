# utils/tradeforge_logger.py
"""
TradeForge Logging Utility
--------------------------
Provides a consistent logger setup across all modules.
Logs to both 'logs/app.log' (file) and terminal console.
Console logs are colorized + use emojis for readability.
"""

import logging
import os
import sys

# --- ANSI color codes ---
COLORS = {
    "DEBUG": "\033[37m",    # White
    "INFO": "\033[36m",     # Cyan
    "SUCCESS": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",    # Red
    "CRITICAL": "\033[41m", # Red background
    "RESET": "\033[0m",     # Reset
}

# --- Emojis per level ---
EMOJIS = {
    "DEBUG": "🐛",
    "INFO": "ℹ️",
    "SUCCESS": "✅",
    "WARNING": "⚠️",
    "ERROR": "❌",
    "CRITICAL": "🔥",
}

# Add custom SUCCESS level (between INFO=20 and WARNING=30)
SUCCESS_LEVEL_NUM = 25
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")

def success(self, message, *args, **kws):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kws)

logging.Logger.success = success


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors + emojis based on log level."""
    def format(self, record):
        levelname = record.levelname
        msg = record.getMessage()

        # Pick emoji + color
        emoji = EMOJIS.get(levelname, "")
        color = COLORS.get(levelname, "")
        reset = COLORS["RESET"]

        # Apply to level + message
        record.levelname = f"{color}{levelname}{reset}"
        record.msg = f"{emoji} {color}{msg}{reset}"

        return super().format(record)


def setup_logger(name=__name__):
    """
    Initializes and returns a logger with file + console output.

    Parameters:
        name (str): Module-specific logger name (typically __name__)

    Returns:
        logging.Logger: Configured logger instance
    """

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Allow all levels

    # Avoid adding duplicate handlers
    if not logger.handlers:
        # --- Formatters ---
        file_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        console_formatter = ColoredFormatter("%(asctime)s | %(levelname)s | %(message)s")

        # --- File Handler (UTF-8 safe) ---
        file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
        file_handler.setFormatter(file_formatter)

        # --- Console Handler (UTF-8 safe + colored + emoji) ---
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
