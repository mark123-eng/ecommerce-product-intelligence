from config.logging_config import setup_logging


logger = setup_logging()

logger.info("Application started successfully.")

logger.warning("This is a test warning.")

logger.error("This is a test error.")