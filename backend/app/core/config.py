import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, "data", "knowledge_base", "dicionario_toon_v2.md")
    
    # --- AQUI ESTÁ A CORREÇÃO ---
    # Usamos o 2.5 Flash Lite (Estável, Rápido e com Cota Alta Gratuita)
    LLM_MODEL = "gemini-2.5-flash-lite"
    
    # Modelo de Embeddings mais novo (suporta chunks maiores e é mais barato/eficiente)
    EMBEDDING_MODEL = "models/text-embedding-004"
    
    TEMPERATURE = 0.0

settings = Settings()