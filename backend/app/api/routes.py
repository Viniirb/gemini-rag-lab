from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import RAGService

router = APIRouter()

class ChatRequest(BaseModel):
    pergunta: str

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        resposta = RAGService.ask(request.pergunta)
        return {"resposta": resposta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

