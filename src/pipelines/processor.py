import json
from ..services.storage import blob_client, queue_client
from ..services.openai_client import call_model
from ..services.db import upsert_result
from ..services.scoring import calculate_confidence
from ..services.logger import get_logger

logger = get_logger()


def process_message(message: dict):
    # message contains doc_id and blob_name
    blob_name = message.get("blob_name")
    doc_id = message.get("doc_id")
    logger.info(f"Start processing {doc_id}")
    blob_data = blob_client.container.download_blob(blob_name).readall()

    # BYPASS OpenAI model calls for local/dev/test: use dummy data
    extracted = {"text": "Sample extracted text for doc_id %s" % doc_id}
    mapped_json = {
        "invoice_number": "INV-%s" % doc_id[:8],
        "date": "2025-11-21",
        "total": 123.45,
        "vendor": "Sample Vendor",
        "line_items": [
            {"desc": "Item 1", "qty": 1, "price": 100},
            {"desc": "Item 2", "qty": 2, "price": 11.725}
        ]
    }
    confidence = 0.95

    result = {
        "doc_id": doc_id,
        "blob_name": blob_name,
        "extracted": extracted,
        "mapped": mapped_json,
        "confidence": confidence,
        "validated": False
    }

    upsert_result(result)
    logger.info(f"Finished processing {doc_id} with confidence {confidence}")
    return result
