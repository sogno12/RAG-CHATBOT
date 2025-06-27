from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.search_service import search_similar_docs

router = APIRouter()

@router.post("/search-doc")
async def search_doc(request: dict):
    query = request.get("query", "")
    if not query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing query")
    results = search_similar_docs(query)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok", "result": results})
