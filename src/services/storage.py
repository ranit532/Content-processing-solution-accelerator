import os
from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueServiceClient

BLOB_CONN = os.getenv("BLOB_CONN", "UseDevelopmentStorage=true")
QUEUE_CONN = os.getenv("QUEUE_CONN", "UseDevelopmentStorage=true")

blob_service = BlobServiceClient.from_connection_string(BLOB_CONN)
queue_service = QueueServiceClient.from_connection_string(QUEUE_CONN)

class BlobClient:
    def __init__(self, container_name="documents"):
        self.container = blob_service.get_container_client(container_name)
        try:
            self.container.create_container()
        except Exception:
            pass

    def upload_blob(self, name: str, data: bytes):
        self.container.upload_blob(name, data, overwrite=True)

    def download_blob(self, name: str) -> bytes:
        blob = self.container.download_blob(name)
        return blob.readall()

class QueueClient:
    def __init__(self, queue_name="processing-queue"):
        self.queue = queue_service.get_queue_client(queue_name)
        try:
            self.queue.create_queue()
        except Exception:
            pass

    def send_message(self, message: dict):
        import json
        self.queue.send_message(json.dumps(message))

    def receive_messages(self, max_messages: int = 10):
        return self.queue.receive_messages()

    def delete_message(self, msg):
        try:
            self.queue.delete_message(msg.id, msg.pop_receipt)
        except Exception:
            pass

blob_client = BlobClient()
queue_client = QueueClient()
