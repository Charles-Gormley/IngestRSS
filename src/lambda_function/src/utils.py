import logging
import os

def setup_logging():
    logger = logging.getLogger()
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    logger.setLevel(logging.getLevelName(log_level))
    return logger