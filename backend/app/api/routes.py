from fastapi import APIRouter, HTTPException
from app.services.rag_service import rag_service
from app.domain.schemas import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        if not request.pergunta.strip():
            raise HTTPException(status_code=400, detail="Pergunta vazia.")

        resposta_texto = rag_service.ask(request.pergunta)
        
        return ChatResponse(resposta=resposta_texto)
        
    except Exception as e:
        print(f"Erro na rota: {e}")
        raise HTTPException(status_code=500, detail="Erro interno.")