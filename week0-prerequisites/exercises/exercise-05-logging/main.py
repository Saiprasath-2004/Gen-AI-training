import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

logger.info("Application started")

logger.warning("Low Disk space")

logger.error("Database connection failed")