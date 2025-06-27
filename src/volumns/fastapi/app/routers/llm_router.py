from fastapi import APIRouter
from app.services.chat_service import llm_health_check, get_llm_status_verbose

router = APIRouter()

@router.get("/llm-status")
def llm_status():
    return llm_health_check()

@router.get("/llm-status/detail")
def llm_status_detail():
    return get_llm_status_verbose()
