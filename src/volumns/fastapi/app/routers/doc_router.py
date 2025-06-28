from fastapi import APIRouter, UploadFile, File, status, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from app.services.doc_service import embed_and_store, get_uploaded_documents, delete_document_by_id, extract_text
from app.utils.logger import logger

router = APIRouter(prefix="/documents", tags=["Document"])

@router.post("/upload-doc")
async def upload_doc(
    file: UploadFile = File(None),
    url: str = Query(None)
):
    logger.info("📄 문서 업로드 요청")
    try:
        content, source = await extract_text(file=file, url=url)
        result = embed_and_store(content, filename=source)
    except HTTPException as e:
        logger.warning(f"❌ 문서 업로드 실패: {e.detail}")
        raise
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ok", "result": result}
    )

# 업로드된 문서 목록 조회
@router.get("")
async def list_documents():
    logger.info("📄 문서 목록 조회")
    docs = get_uploaded_documents()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ok", "documents": docs}
    )

# 특정 문서 삭제
@router.delete("/{source}")
async def delete_document(source: str, request: Request):
    body = await request.json()
    uuid = body.get("uuid")
    if not uuid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing query")
    
    logger.info(f"🗑️ 문서 삭제 요청: source={source}, uuid={uuid}")
    delete_document_by_id(uuid)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ok", "message": f"document {uuid} deleted"}
    )