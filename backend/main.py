import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain

load_dotenv()

rag_chain = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_chain
    print("--- INICIANDO SERVIDOR RAG ---")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: API Key não encontrada.")
        yield
        return
    
    caminho_pdf = os.path.join("documentos", "Jon Erickson - Hacking Art of Exploitation.pdf")

    print("Carregando documento PDF e Gerando Embeddings...")
    try:
        loader = PyPDFLoader(caminho_pdf)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        vectorstore = FAISS.from_documents(splits, embeddings)
        retriever = vectorstore.as_retriever()

        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
        system_prompt = (
            "Você é um assistente especialista em segurança cibernética. "
            "Use o contexto abaixo para responder. Se não souber, diga que não sabe. "
            "Responda em português."
            "\n\nContexto:\n{context}"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        print("✅ RAG PRONTO! API DISPONÍVEL.")

    except Exception as e:
            print(f"Erro ao configurar o RAG: {e}")
    yield
    print("--- SERVIDOR RAG FINALIZADO ---")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    pergunta: str

@app.get("/")
def home():
     return {"status": "IA Online", "model": "Gemini 2.5 Flash"}

@app.post("/chat")
def chat(request: ChatRequest):
    if not rag_chain:
        raise HTTPException(status_code=500, detail="A IA ainda não foi inicializada.")
    try:
        response = rag_chain.invoke({"input": request.pergunta})
        return {"resposta": response['answer']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar a pergunta: {e}")