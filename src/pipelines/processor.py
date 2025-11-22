import io
import pdfplumber
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

    # Real PDF extraction using pdfplumber
    with pdfplumber.open(io.BytesIO(blob_data)) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # Simple parsing logic for demo (customize for your invoice format)
    import re
    invoice_number = re.search(r"Invoice Number[:\s]+([A-Za-z0-9-]+)", text)
    date = re.search(r"Date[:\s]+([0-9-]+)", text)
    total = re.search(r"Total[:\s]+\$?([0-9.]+)", text)
    vendor = re.search(r"Vendor[:\s]+([A-Za-z0-9 ]+)", text)

    # Line items parsing (demo: looks for lines like 'Item X: Qty Y @ $Z')
    line_items = []
    for match in re.finditer(r"Item (\d+): Qty (\d+) @ \$([0-9.]+)", text):
        desc = f"Item {match.group(1)}"
        qty = int(match.group(2))
        price = float(match.group(3))
        line_items.append({"desc": desc, "qty": qty, "price": price})

    mapped_json = {
        "invoice_number": invoice_number.group(1) if invoice_number else None,
        "date": date.group(1) if date else None,
        "total": float(total.group(1)) if total else None,
        "vendor": vendor.group(1) if vendor else None,
        "line_items": line_items
    }

    # Confidence score: simple heuristic (number of fields found)
    found_fields = sum([invoice_number is not None, date is not None, total is not None, vendor is not None, len(line_items) > 0])
    confidence = found_fields / 5.0

    result = {
        "id": doc_id,
        "doc_id": doc_id,
        "blob_name": blob_name,
        "extracted": {"text": text},
        "mapped": mapped_json,
        "confidence": confidence,
        "validated": False,
        "partitionKey": doc_id
    }

    print("[DEBUG] Upserting to Cosmos DB. Document:")
    print(result)
    upsert_result(result)
    logger.info(f"Finished processing {doc_id} with confidence {confidence}")
    return result
