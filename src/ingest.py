"""
ingest.py
---------
Script de ingestão: lê o CSV de leituras de temperatura de dispositivos IoT
e insere os dados na tabela 'temperature_readings' do PostgreSQL.

Autor: <seu nome>
Disciplina: Disruptive Architectures - IoT, Big Data e IA
"""

import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

# ---------------------------------------------------------------
# 1. CONFIGURAÇÕES
# ---------------------------------------------------------------

# Caminho do arquivo CSV (relativo à raiz do projeto)
CSV_PATH = "data/IOT-temp.csv"

# String de conexão com o PostgreSQL
# Formato: postgresql://USUARIO:SENHA@HOST:PORTA/NOME_DO_BANCO
DB_URL = "postgresql://postgres:suasenha@localhost:5432/iot_db"

# Nome da tabela de destino
TABLE_NAME = "temperature_readings"


# ---------------------------------------------------------------
# 2. FUNÇÃO PARA LER E TRATAR O CSV
# ---------------------------------------------------------------

def load_and_clean_csv(path: str) -> pd.DataFrame:
    """
    Lê o CSV, renomeia as colunas para nomes amigáveis e converte tipos.
    """
    print(f"[1/4] Lendo o CSV: {path}")
    df = pd.read_csv(path)

    # Renomear colunas para nomes que combinam com a tabela do banco
    df = df.rename(columns={
        "id": "original_id",           # guardamos o id original só por segurança
        "room_id/id": "device_id",     # dispositivo
        "noted_date": "reading_datetime",  # data/hora da leitura
        "temp": "temperature",         # temperatura
        "out/in": "location",          # dentro ou fora
    })

    # Converter a coluna de data para o tipo datetime
    # ATENÇÃO: o formato é DD-MM-YYYY HH:MM (dia primeiro), por isso dayfirst=True
    print("[2/4] Convertendo a coluna de data (formato DD-MM-YYYY)...")
    df["reading_datetime"] = pd.to_datetime(
        df["reading_datetime"],
        format="%d-%m-%Y %H:%M",
        errors="coerce"
    )

    # Padronizar a coluna location (In / Out) para minúsculo
    df["location"] = df["location"].str.lower()

    # Gerar um id numérico sequencial (1, 2, 3, ...) para a chave primária
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

    # Selecionar apenas as colunas que vamos inserir no banco
    df_final = df[["id", "device_id", "reading_datetime", "temperature", "location"]]

    print(f"    -> {len(df_final)} linhas prontas para inserir.")
    return df_final


# ---------------------------------------------------------------
# 3. FUNÇÃO PARA INSERIR NO BANCO
# ---------------------------------------------------------------

def insert_into_postgres(df: pd.DataFrame, db_url: str, table: str) -> None:
    """
    Conecta no PostgreSQL via SQLAlchemy e insere o DataFrame na tabela.
    """
    print(f"[3/4] Conectando ao banco e inserindo os dados...")

    # Cria o engine do SQLAlchemy
    engine = create_engine(db_url)

    # Limpar a tabela antes de inserir (evita duplicatas se rodar 2x)
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table};"))

    # Inserir o DataFrame. chunksize ajuda em bases grandes.
    df.to_sql(
        name=table,
        con=engine,
        if_exists="append",  # já criamos a tabela antes, então só adiciona
        index=False,
        chunksize=5000,
        method="multi",
    )

    print(f"    -> {len(df)} linhas inseridas com sucesso!")


# ---------------------------------------------------------------
# 4. PROGRAMA PRINCIPAL
# ---------------------------------------------------------------

def main():
    inicio = datetime.now()
    print("=" * 60)
    print(" INGESTÃO DE DADOS IoT -> PostgreSQL")
    print("=" * 60)

    df = load_and_clean_csv(CSV_PATH)
    insert_into_postgres(df, DB_URL, TABLE_NAME)

    duracao = datetime.now() - inicio
    print("[4/4] Concluído!")
    print(f"Tempo total: {duracao.total_seconds():.2f} segundos")
    print("=" * 60)


if __name__ == "__main__":
    main()