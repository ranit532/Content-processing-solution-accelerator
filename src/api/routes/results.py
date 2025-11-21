from fastapi import APIRouter, HTTPException, Depends
from ..services.db import get_result_by_id, list_results
from ..services.logger import get_logger
from ..services.auth import require_api_key
from ..services.evaluator import evaluate_mapping

logger = get_logger()
router = APIRouter()

@router.get("/{doc_id}", dependencies=[Depends(require_api_key)])
async def get_results(doc_id: str):
    res = get_result_by_id(doc_id)
    if not res:
        raise HTTPException(status_code=404, detail="Not found")
    # compute evaluation
    mapped = res.get('mapped', {})
    eval_res = evaluate_mapping(mapped)
    res['evaluation'] = eval_res
    return res

@router.get("/", dependencies=[Depends(require_api_key)])
async def get_history():
    items = list_results()
    # attach basic evaluation summary
    for i in items:
        i['evaluation'] = evaluate_mapping(i.get('mapped', {}))
    return items
