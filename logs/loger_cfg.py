from datetime import datetime
from loguru import logger

log_file = f"logs_info/log_{datetime.now().strftime('%Y-%m-%d')}.log"
logger.add(log_file, format="{time} [{level}] - {message}", rotation="10 MB")