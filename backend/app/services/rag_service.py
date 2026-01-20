import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_classic.text_splitter import CharacterTextSplitter
from langchain_classic.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

class RAGService:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.doc_path = os.path.join(base_dir, "data", "knowledge_base", "dicionario_toon_v2.md")

        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vecto_store = None

        self.load_knowledge_base()

    def load_knowledge_base(self):
        """Lê o arquivo Markdown e cria o índice vetorial"""
        if not os.path.exists(self.doc_path):
            print(f"⚠️ Alerta: Arquivo de conhecimento não encontrado em {self.doc_path}")
            print("Rode o script 'gerar_dicionario.py' primeiro!")
            return
        
        loader = TextLoader(self.doc_path, encoding="utf-8")
        documents = loader.load()

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)

        self.vector_store = FAISS.from_documents(texts, self.embeddings)
        print("✅ Base de Conhecimento Carregada com Sucesso!")
    
    def ask(self, question: str):
        if not self.vector_store:
            return "O sistema ainda não mapeou o banco de dados. Por favor, execute o script de mapeamento."
        
        retriever = self.vector_store.as_retriever()
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever
        )

        response = qa_chain.invoke({"query": question})
        return response["result"]

rag_service = RAGService()