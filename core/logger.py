from loguru import logger
import sys

logger.remove()

logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

logger.add("logs/app.log", rotation="500 MB", level="INFO", compression="zip")