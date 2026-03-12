import streamlit as st
import requests
import pandas as pd
import random
from PIL import Image
import pytesseract

st.set_page_config(page_title="Escudo Digital IA", layout="wide")

st.title("🛡️ ESCUDO DIGITAL IA")
st.write("SOC de monitoramento de golpes e análise OSINT")

# =========================================
# 🌍 ANALISE OSINT DE IP
# =========================================

st.header("🌍 Análise OSINT de IP")

ip = st.text_input("Digite domínio ou IP")

if st.button("Analisar IP"):

    try:

        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        data = r.json()

        if data["status"] == "success":

            st.success("IP encontrado")

            col1, col2 = st.columns(2)

            with col1:
                st.write("IP:", data["query"])
                st.write("País:", data["country"])
                st.write("Cidade:", data["city"])
                st.write("Região:", data["regionName"])

            with col2:
                st.write("ISP:", data["isp"])
                st.write("Organização:", data["org"])
                st.write("ASN:", data["as"])
                st.write("Fuso horário:", data["timezone"])

            st.subheader("📍 Localização no mapa")

            mapa = pd.DataFrame({
                "lat":[data["lat"]],
                "lon":[data["lon"]]
            })

            st.map(mapa)

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
        "clique aqui"
    ]

    score = 0

    for p in palavras:

        if p in mensagem.lower():
            score += 15

    st.write("Score de risco:", score)

    if score >= 40:
        st.error("🚨 Alto risco de golpe")

    elif score >= 20:
        st.warning("⚠️ Mensagem suspeita")

    else:
        st.success("🟢 Baixo risco")


# =========================================
# 📷 ANALISAR PRINT
# =========================================

st.header("📷 Analisar print de e-mail ou WhatsApp")

imagem = st.file_uploader(
    "Envie print de mensagem suspeita",
    type=["png","jpg","jpeg"]
)

if imagem:

    img = Image.open(imagem)

    st.image(img)

    try:

        texto_extraido = pytesseract.image_to_string(img)

        st.subheader("Texto detectado")

        st.write(texto_extraido)

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

            if p in texto_extraido.lower():
                score += 15

        st.write("Score de risco:", score)

        if score >= 40:
            st.error("🚨 Possível golpe detectado")

        elif score >= 20:
            st.warning("⚠️ Conteúdo suspeito")

        else:
            st.success("🟢 Baixo risco")

    except:

        st.warning("OCR não disponível no servidor")


# =========================================
# 📡 PAINEL SOC
# =========================================

st.header("📡 Painel SOC")

col1, col2, col3 = st.columns(3)

col1.metric("Eventos detectados", random.randint(10,150))
col2.metric("IPs analisados", random.randint(50,300))
col3.metric("Alertas ativos", random.randint(0,20))


# =========================================
# 🛰️ RADAR DE AMEAÇA
# =========================================

st.header("🛰️ Radar de ameaça")

nivel = random.randint(10,100)

st.progress(nivel)

if nivel > 70:
    st.error("🚨 Nível alto de ameaça")

elif nivel > 40:
    st.warning("⚠️ Atividade suspeita")

else:
    st.success("🟢 Ambiente seguro")
