import os
import time
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from langchain_google_genai import ChatGoogleGenerativeAI
from toon_format import encode

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"mssql+pyodbc://{DB_HOST}/{DB_NAME}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
    "&TrustServerCertificate=yes"
)

llm = ChatGoogleGenerativeAI(model="gemma-3-27b-it", temperature=0.0)

def preparar_dados_para_toon(df):
    """
    Prepara o DataFrame para o TOON:
    1. Trunca textos gigantes (Economia de Tokens)
    2. Converte para lista de dicionários (Formato nativo do toon-python)
    """
    if df.empty:
        return []
    
    df_limpo = df.astype(str).map(lambda x: (x[:100] + '...') if len(x) > 100 else x)
    return df_limpo.to_dict(orient='records')

def main():
    print(f"--- 🐍 Iniciando Análise com toon-python: {DB_NAME} ---")

    try:
        engine = create_engine(DATABASE_URL, fast_executemany=True)
        connection = engine.connect()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return
    
    print(f"Total de tabelas encontradas: {len(tables)}")
    final_docs = f"# Dicionário TOON (Oficial): {DB_NAME}\n\n"

    for i, table in enumerate(tables):
        print(f"[{i+1}/{len(tables)}] Processando: {table}...")

        try:
            query = text(f"SELECT TOP 3 * FROM {table}")
            df = pd.read_sql(query, connection)

            dados_lista = preparar_dados_para_toon(df)

            if not dados_lista:
                print(f"   (Tabela vazia, pulando...)")
                continue
            
            toon_string = encode(dados_lista)
        except Exception as e:
            print(f"   Erro ao obter dados da tabela {table}: {e}")
            continue

        prompt = f"""
        Analise os dados abaixo que estão no formato TOON (Token-Oriented Object Notation).
        
        TABELA: '{table}'
        
        DADOS TOON:
        {toon_string}

        TAREFA:
        Responda APENAS um bloco Markdown com:
        1. **Nome Funcional**: (Nome humanizado)
        2. **Descrição**: (Resumo de 1 frase)
        3. **Glossário**: (Tradução de siglas ex: CD_CLI -> Código Cliente)
        """

        try:
            response = llm.invoke(prompt)
            final_docs += f"## {table}\n{response.content}\n\n---\n"
            time.sleep(4)
        except Exception as e:
            print(f"   ⚠️ Erro na API: {e}")
            time.sleep(10)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(base_dir, "data", "knowledge_base", "dicionario_toon_v2.md")
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_docs)  
    
    print(f"✅ Sucesso! Arquivo gerado em: {output_file}")

if __name__ == "__main__":
    main()