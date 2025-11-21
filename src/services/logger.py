import logging
import sys

LOG_LEVEL = logging.DEBUG

logger = logging.getLogger("content_processor")
logger.setLevel(LOG_LEVEL)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)


def get_logger():
    return logger
