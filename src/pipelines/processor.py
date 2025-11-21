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

    # step 1: OCR / text extraction via OpenAI or local OCR
    ocr_prompt = "Extract text, tables and key-value pairs from the document. Return JSON with fields: text, tables"
    try:
        ocr_resp = call_model(ocr_prompt, image_bytes=blob_data)
        extracted_text = str(ocr_resp)
    except Exception as e:
        logger.exception("OCR model failed")
        extracted_text = ""

    extracted = {"text": extracted_text}

    # step 2: Schema mapping using prompt templates
    mapping_prompt = "Map extracted content to invoice schema: invoice_number, date, total, vendor, line_items. Respond with JSON only."
    try:
        mapping_resp = call_model(mapping_prompt + "\n\nContent:\n" + extracted.get("text", ""))
        mapped_json = json.loads(str(mapping_resp)) if isinstance(mapping_resp, (str,)) else mapping_resp
    except Exception as e:
        logger.exception("Mapping model failed")
        mapped_json = {"error": "mapping_failed"}

    # compute confidence
    confidence = calculate_confidence(extracted, mapped_json)

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
