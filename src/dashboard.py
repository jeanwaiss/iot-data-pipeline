"""
dashboard.py
------------
Dashboard interativo em Streamlit para visualização dos dados de
temperatura de dispositivos IoT armazenados no PostgreSQL.

Autor: <seu nome>
Disciplina: Disruptive Architectures - IoT, Big Data e IA

Como executar:
    streamlit run src/dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# === 1. CONFIGURAÇÕES ===

# String de conexão com o PostgreSQL (mesma do script de ingestão)
DB_URL = "postgresql://postgres:suasenha@localhost:5432/iot_db"

# Título da página do navegador
st.set_page_config(
    page_title="Dashboard IoT - Temperaturas",
    page_icon="🌡️",
    layout="wide",
)

# === 2. CONEXÃO COM O BANCO ===

@st.cache_resource
def get_engine():
    """Cria o engine do SQLAlchemy (cacheado para não reconectar sempre)."""
    return create_engine(DB_URL)


@st.cache_data(ttl=600)
def load_data(view_name: str) -> pd.DataFrame:
    """Carrega os dados de uma view do PostgreSQL como DataFrame."""
    engine = get_engine()
    return pd.read_sql(f"SELECT * FROM {view_name}", engine)


# === 3. CABEÇALHO ===

st.title("🌡️ Dashboard de Temperaturas IoT")
st.markdown(
    "Visualização das leituras de temperatura coletadas por dispositivos IoT "
    "e armazenadas no PostgreSQL."
)
st.markdown("---")

# === 4. KPIs NO TOPO ===

df_kpi = load_data("avg_temp_por_localizacao")
df_disp = load_data("avg_temp_por_dispositivo")
df_hora = load_data("leituras_por_hora")
df_dia = load_data("temp_max_min_por_dia")

total_leituras = int(df_hora["contagem"].sum())
temp_media_geral = round(df_disp["avg_temp"].mean(), 2)
num_dispositivos = df_disp["device_id"].nunique()
num_dias = df_dia["data"].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("📊 Total de Leituras", f"{total_leituras:,}")
col2.metric("🌡️ Temp. Média Geral", f"{temp_media_geral} °C")
col3.metric("📡 Dispositivos", num_dispositivos)
col4.metric("📅 Dias Cobertos", num_dias)

st.markdown("---")

# === 5. GRÁFICO 1: MÉDIA POR LOCALIZAÇÃO (IN vs OUT) ===

st.header("📍 Média de Temperatura por Localização (In vs Out)")

fig1 = px.bar(
    df_kpi,
    x="location",
    y="avg_temp",
    text="avg_temp",
    color="location",
    labels={"location": "Localização", "avg_temp": "Temperatura Média (°C)"},
    color_discrete_map={"in": "#1f77b4", "out": "#ff7f0e"},
)
fig1.update_traces(texttemplate="%{text} °C", textposition="outside")
fig1.update_layout(showlegend=False, height=400)
st.plotly_chart(fig1, use_container_width=True)

# === 6. GRÁFICO 2: MÉDIA POR DISPOSITIVO ===

st.header("📡 Média de Temperatura por Dispositivo")

fig2 = px.bar(
    df_disp,
    x="device_id",
    y="avg_temp",
    text="avg_temp",
    labels={"device_id": "Dispositivo", "avg_temp": "Temperatura Média (°C)"},
)
fig2.update_traces(texttemplate="%{text} °C", textposition="outside")
fig2.update_layout(height=400)
st.plotly_chart(fig2, use_container_width=True)

# === 7. GRÁFICO 3: LEITURAS POR HORA DO DIA ===

st.header("🕒 Leituras por Hora do Dia")

fig3 = px.line(
    df_hora,
    x="hora",
    y="contagem",
    markers=True,
    labels={"hora": "Hora do Dia", "contagem": "Quantidade de Leituras"},
)
fig3.update_layout(height=400)
st.plotly_chart(fig3, use_container_width=True)

# === 8. GRÁFICO 4: TEMPERATURAS MÁX/MÍN POR DIA ===

st.header("📅 Temperaturas Máximas e Mínimas por Dia")

# Transformar em formato "long" para o Plotly desenhar duas linhas
df_dia_long = df_dia.melt(
    id_vars="data",
    value_vars=["temp_max", "temp_min"],
    var_name="tipo",
    value_name="temperatura",
)
df_dia_long["tipo"] = df_dia_long["tipo"].map(
    {"temp_max": "Máxima", "temp_min": "Mínima"}
)

fig4 = px.line(
    df_dia_long,
    x="data",
    y="temperatura",
    color="tipo",
    labels={"data": "Data", "temperatura": "Temperatura (°C)", "tipo": "Tipo"},
    color_discrete_map={"Máxima": "#d62728", "Mínima": "#2ca02c"},
)
fig4.update_layout(height=450)
st.plotly_chart(fig4, use_container_width=True)

# === 9. RODAPÉ ===

st.markdown("---")
st.caption(
    "Projeto desenvolvido para a disciplina **Disruptive Architectures: "
    "IoT, Big Data e IA**. Pipeline: CSV → Python → PostgreSQL → Streamlit."
)