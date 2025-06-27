from fastapi import APIRouter, UploadFile, File, status
from fastapi.responses import JSONResponse
from app.services.embed_service import embed_and_store

router = APIRouter()

@router.post("/upload-doc")
async def upload_doc(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename
    result = embed_and_store(content.decode("utf-8"), filename=filename)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok", "result": result})
