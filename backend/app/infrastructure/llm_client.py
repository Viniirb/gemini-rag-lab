from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from app.core.config import settings

class LLMClient:
    @staticmethod
    def get_llm():
        """Retorna a instância configurada do Chat Model"""
        return ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL, 
            temperature=settings.TEMPERATURE
        )

    @staticmethod
    def get_embeddings():
        """Retorna a instância configurada dos Embeddings"""
        return GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL
        )