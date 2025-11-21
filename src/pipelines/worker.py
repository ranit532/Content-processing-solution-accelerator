import time
from ..services.storage import queue_client
from ..pipelines.processor import process_message
from ..services.logger import get_logger
import json

logger = get_logger()


def run_worker():
    logger.info("Worker started")
    while True:
        messages = queue_client.queue.receive_messages()
        for msg in messages:
            try:
                body = json.loads(msg.content)
                logger.info(f"Processing message {body}")
                process_message(body)
                queue_client.queue.delete_message(msg)
            except Exception as e:
                logger.exception("Failed to process message")
        time.sleep(5)


if __name__ == '__main__':
    run_worker()
