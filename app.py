
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import datetime
import os
import time

# Configuracoes do banco de dados
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "senha123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "pedidos_db")

# Conexao com o PostgreSQL
engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}",
    pool_pre_ping=True
)

# Criacao da tabela de pedidos
def init_db():
    for tentativa in range(10):
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS pedidos (
                        id SERIAL PRIMARY KEY,
                        data DATE,
                        hora TIME,
                        solicitante VARCHAR(100),
                        assunto VARCHAR(255),
                        descricao TEXT,
                        prioridade VARCHAR(50)
                    )
                """))
            return
        except Exception:
            if tentativa == 9:
                raise
            time.sleep(2)

# Inicializar banco
try:
    init_db()
except Exception as e:
    st.error(f"Erro ao conectar ao banco: {e}")
    st.stop()

# Interface
st.title("Cadastro de Pedidos")
st.write("Sistema de cadastro e gerenciamento de pedidos")

# Formulario
st.subheader("Novo Pedido")

with st.form("cadastro_form"):

    data = st.date_input(
        "Data",
        datetime.date.today()
    )

    hora = st.time_input(
        "Hora",
        datetime.datetime.now().time()
    )

    solicitante = st.text_input("Solicitante")

    assunto = st.text_input("Assunto")

    descricao = st.text_area("Descricao")

    prioridade = st.selectbox(
        "Prioridade",
        ["Baixa", "Média", "Alta"]
    )

    submit_button = st.form_submit_button(
        label="Cadastrar Pedido"
    )

# Salvar pedido no banco
if submit_button:

    if solicitante.strip() and assunto.strip():

        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO pedidos (
                        data,
                        hora,
                        solicitante,
                        assunto,
                        descricao,
                        prioridade
                    )
                    VALUES (
                        :data,
                        :hora,
                        :solicitante,
                        :assunto,
                        :descricao,
                        :prioridade
                    )
                """), {
                    "data": data,
                    "hora": hora,
                    "solicitante": solicitante.strip(),
                    "assunto": assunto.strip(),
                    "descricao": descricao,
                    "prioridade": prioridade
                })

            st.success("Pedido cadastrado com sucesso!")

        except Exception as e:
            st.error(f"Erro ao cadastrar pedido: {e}")

    else:
        st.error(
            "Preencha os campos Solicitante e Assunto."
        )

# Visualizacao dos pedidos
st.subheader("Pedidos Cadastrados")

try:
    with engine.connect() as conn:
        pedidos_df = pd.read_sql_query(
            text("SELECT * FROM pedidos ORDER BY id DESC"),
            con=conn
        )

    st.dataframe(
        pedidos_df,
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.error(f"Erro ao carregar pedidos: {e}")
