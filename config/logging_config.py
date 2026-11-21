import logging

from pathlib import Path


# Locate the project root directory.
BASE_DIR = Path(__file__).resolve().parent.parent

# Define the logs directory.
LOG_DIR = BASE_DIR / "logs"

# Define the application log file.
LOG_FILE = LOG_DIR / "application.log"


def setup_logging():
    """
    Configures application logging.

    Logs are written to:
    1. The terminal.
    2. A permanent application.log file.
    """

    # Create logs directory if it does not exist.
    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Create the application logger.
    logger = logging.getLogger("ecommerce_intelligence")

    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers.
    if logger.handlers:
        return logger

    # Define log message format.
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Create file handler.
    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )

    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Create terminal handler.
    console_handler = logging.StreamHandler()

    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Attach handlers to logger.
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger