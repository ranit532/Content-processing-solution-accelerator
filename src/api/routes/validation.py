from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.db import update_result_validation, get_result_by_id
from services.auth import require_api_key
from services.logger import get_logger

logger = get_logger()

class ValidationPayload(BaseModel):
    changes: dict

router = APIRouter()

@router.post("/{doc_id}", dependencies=[Depends(require_api_key)])
async def submit_validation(doc_id: str, payload: ValidationPayload):
    res = get_result_by_id(doc_id)
    if not res:
        raise HTTPException(status_code=404, detail="Not found")
    update_result_validation(doc_id, payload.changes)
    logger.info(f"Validated {doc_id}")
    return {"status": "accepted"}
