from pydantic import BaseModel

class ChatRequest(BaseModel):
    pergunta: str

class ChatResponse(BaseModel):
    resposta: str