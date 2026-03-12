import streamlit as st
import requests
import pandas as pd
import random
import json
import os
from datetime import datetime
from PIL import Image
import pytesseract
from urllib.parse import urlparse

st.set_page_config(page_title="Escudo Digital IA", layout="wide")

st.title("🛡️ ESCUDO DIGITAL IA")
st.write("SOC de monitoramento de golpes e análise OSINT")

# =========================================
# BANCO DE EVENTOS
# =========================================

ARQUIVO_EVENTOS = "golpes_detectados.json"

if not os.path.exists(ARQUIVO_EVENTOS):
    with open(ARQUIVO_EVENTOS, "w", encoding="utf-8") as f:
        json.dump([], f)

def salvar_evento(tipo, conteudo, score):
    try:
        with open(ARQUIVO_EVENTOS, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except:
        dados = []

    dados.append({
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "tipo": tipo,
        "conteudo": conteudo,
        "score": score
    })

    with open(ARQUIVO_EVENTOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def carregar_eventos():
    try:
        with open(ARQUIVO_EVENTOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

eventos = carregar_eventos()

# =========================================
# 🌍 ANÁLISE OSINT DE IP
# =========================================

st.header("🌍 Análise OSINT de IP")

ip = st.text_input("Digite domínio ou IP")

if st.button("Analisar IP"):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        data = r.json()

        if data.get("status") == "success":
            st.success("IP encontrado")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**IP:**", data.get("query", "N/A"))
                st.write("**País:**", data.get("country", "N/A"))
                st.write("**Cidade:**", data.get("city", "N/A"))
                st.write("**Região:**", data.get("regionName", "N/A"))

            with col2:
                st.write("**ISP:**", data.get("isp", "N/A"))
                st.write("**Organização:**", data.get("org", "N/A"))
                st.write("**ASN:**", data.get("as", "N/A"))
                st.write("**Fuso horário:**", data.get("timezone", "N/A"))

            mapa = pd.DataFrame({
                "lat": [data["lat"]],
                "lon": [data["lon"]]
            })

            st.subheader("📍 Localização no mapa")
            st.map(mapa)

            salvar_evento(
                "ip",
                f'{data.get("query","")} | {data.get("country","")} | {data.get("city","")} | {data.get("org","")}',
                10
            )

            eventos = carregar_eventos()

        else:
            st.error("Não foi possível localizar o IP")

    except:
        st.error("Erro ao consultar IP")

# =========================================
# 🚨 DETECTOR DE PHISHING
# =========================================

st.header("🚨 Detector de Phishing")

mensagem = st.text_area("Cole mensagem ou link suspeito")

if st.button("Analisar mensagem"):
    palavras = [
        "pix",
        "senha",
        "codigo",
        "urgente",
        "transferencia",
        "banco",
        "login",
        "verificacao",
        "confirmar",
        "clique aqui",
        "atualize conta"
    ]

    score = 0

    for p in palavras:
        if p in mensagem.lower():
            score += 15

    st.write("**Score de risco:**", score)

    if score >= 40:
        st.error("🚨 Alto risco de golpe")
    elif score >= 20:
        st.warning("⚠️ Mensagem suspeita")
    else:
        st.success("🟢 Baixo risco")

    salvar_evento("mensagem", mensagem[:300], score)
    eventos = carregar_eventos()

# =========================================
# 🔎 SCANNER DE DOMÍNIO
# =========================================

st.header("🔎 Scanner de domínio")

link = st.text_input("Digite URL suspeita")

if st.button("Analisar domínio"):
    try:
        dominio = urlparse(link).netloc if "://" in link else link

        r = requests.get(f"http://ip-api.com/json/{dominio}", timeout=10)
        data = r.json()

        if data.get("status") == "success":
            st.write("**Domínio:**", dominio)
            st.write("**País:**", data.get("country", "N/A"))
            st.write("**ISP:**", data.get("isp", "N/A"))
            st.write("**ASN:**", data.get("as", "N/A"))

            score = 15
            salvar_evento("dominio", dominio, score)
            eventos = carregar_eventos()

        else:
            st.error("Domínio não encontrado")

    except:
        st.error("Erro na análise")

# =========================================
# 📷 ANÁLISE DE PRINT
# =========================================

st.header("📷 Analisar print de e-mail ou WhatsApp")

imagem = st.file_uploader(
    "Envie print suspeito",
    type=["png", "jpg", "jpeg"]
)

if imagem:
    img = Image.open(imagem)
    st.image(img)

    try:
        texto = pytesseract.image_to_string(img)

        st.subheader("Texto detectado")
        st.write(texto)

        palavras = [
            "pix",
            "senha",
            "codigo",
            "urgente",
            "transferencia",
            "banco",
            "login",
            "verificacao",
            "confirmar"
        ]

        score = 0

        for p in palavras:
            if p in texto.lower():
                score += 15

        st.write("**Score de risco:**", score)

        if score >= 40:
            st.error("🚨 Possível golpe detectado")
        elif score >= 20:
            st.warning("⚠️ Conteúdo suspeito")
        else:
            st.success("🟢 Baixo risco")

        salvar_evento("imagem", texto[:300], score)
        eventos = carregar_eventos()

    except:
        st.warning("OCR não disponível no servidor")

# =========================================
# 📊 HISTÓRICO SOC
# =========================================

st.header("📊 Histórico SOC")

if eventos:
    df = pd.DataFrame(eventos)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nenhum evento registrado ainda.")

# =========================================
# 📈 GRÁFICO DE EVENTOS
# =========================================

st.header("📈 Gráfico de eventos")

if eventos:
    df_chart = pd.DataFrame(eventos)
    resumo = df_chart["tipo"].value_counts().reset_index()
    resumo.columns = ["Tipo", "Quantidade"]
    st.bar_chart(resumo.set_index("Tipo"))
else:
    st.info("Sem dados para gráfico.")

# =========================================
# 📡 PAINEL SOC
# =========================================

st.header("📡 Painel SOC")

total_eventos = len(eventos)
alertas_ativos = sum(1 for e in eventos if e["score"] >= 40)
eventos_suspeitos = sum(1 for e in eventos if e["score"] >= 20)

col1, col2, col3 = st.columns(3)

col1.metric("Eventos detectados", total_eventos)
col2.metric("Eventos suspeitos", eventos_suspeitos)
col3.metric("Alertas ativos", alertas_ativos)

# =========================================
# 🛰️ RADAR DE AMEAÇA
# =========================================

st.header("🛰️ Radar de ameaça")

if total_eventos == 0:
    nivel = 10
else:
    media_score = sum(e["score"] for e in eventos) / total_eventos
    nivel = min(100, int(media_score * 2))

st.progress(nivel)

if nivel > 70:
    st.error("🚨 Nível alto de ameaça")
elif nivel > 40:
    st.warning("⚠️ Atividade suspeita")
else:
    st.success("🟢 Ambiente seguro")
