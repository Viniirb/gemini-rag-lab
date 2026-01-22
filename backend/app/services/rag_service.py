import os
import time
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_classic.chains import RetrievalQA

from app.core.config import settings
from app.infrastructure.llm_client import LLMClient

class RAGService:
    def __init__(self):
        self.doc_path = settings.KNOWLEDGE_BASE_PATH
        self.llm = LLMClient.get_llm()
        self.embeddings = LLMClient.get_embeddings()
        self.vector_store = None
        
        self._init_knowledge_base()

    def _init_knowledge_base(self):
        if not os.path.exists(self.doc_path):
            print(f"⚠️ RAG Service: Base não encontrada em {self.doc_path}")
            return

        try:
            print("🔄 Iniciando processamento da Base de Conhecimento...")
            loader = TextLoader(self.doc_path, encoding="utf-8")
            documents = loader.load()
            
            # O Recursive tenta quebrar primeiro por seções (##), depois parágrafos.
            # Isso garante que não tenhamos chunks de 26.000 caracteres.
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=100,
                separators=["\n## ", "\n\n", "\n", " ", ""]
            )
            texts = splitter.split_documents(documents)
            print(f"📊 Documento quebrado em {len(texts)} fragmentos.")

            # Se tentarmos indexar tudo de uma vez, tomamos erro 429.
            # Vamos indexar de 30 em 30 e pausar um pouco.
            
            batch_size = 30
            total_batches = len(texts) // batch_size + 1
            
            # Cria o banco com o primeiro lote para inicializar
            if texts:
                print("🚀 Criando índice vetorial (pode demorar uns segundos)...")
                first_batch = texts[:batch_size]
                self.vector_store = FAISS.from_documents(first_batch, self.embeddings)
                
                # Adiciona o resto em loop com pausa
                for i in range(batch_size, len(texts), batch_size):
                    batch = texts[i : i + batch_size]
                    if batch:
                        self.vector_store.add_documents(batch)
                        print(f"   ⏳ Processando lote {i//batch_size + 1}/{total_batches}...", end="\r")
                        time.sleep(1.5) # Pausa estratégica para a API respirar

            print("\n✅ RAG Service: Indexação concluída com sucesso!")
            
        except Exception as e:
            print(f"\n❌ RAG Service Erro Crítico: {e}")

    def ask(self, question: str) -> str:
        if not self.vector_store:
            return "Erro: O sistema está recarregando a base de conhecimento ou ela está offline."

        try:
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                # Traz 4 contextos
                retriever=self.vector_store.as_retriever(search_kwargs={"k": 4}) 
            )
            return qa_chain.invoke({"query": question})["result"]
            
        except Exception as e:
            return f"Erro ao processar: {str(e)}"

rag_service = RAGService()