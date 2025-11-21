from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Header
from uuid import uuid4
import os
from services.storage import blob_client, queue_client
from services.logger import get_logger
from services.auth import require_api_key

logger = get_logger()

router = APIRouter()

@router.post("/", dependencies=[Depends(require_api_key)])
async def ingest_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    doc_id = str(uuid4())
    # store file to blob
    content = await file.read()
    blob_name = f"documents/{doc_id}/{file.filename}"
    try:
        blob_client.upload_blob(name=blob_name, data=content)
    except Exception as e:
        logger.exception("Failed to upload to blob")
        raise HTTPException(status_code=500, detail="Storage error")
    # enqueue processing
    try:
        queue_client.send_message({"doc_id": doc_id, "blob_name": blob_name})
    except Exception:
        logger.exception("Failed to enqueue message")
        raise HTTPException(status_code=500, detail="Queue error")
    logger.info(f"Enqueued document {doc_id}")
    return {"doc_id": doc_id, "blob_name": blob_name}
