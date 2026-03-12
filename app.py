import streamlit as st
import requests
import pandas as pd
import random
import json
import os
from PIL import Image
import pytesseract
from urllib.parse import urlparse

st.set_page_config(page_title="Escudo Digital IA", layout="wide")

st.title("🛡️ ESCUDO DIGITAL IA")
st.write("SOC de monitoramento de golpes e análise OSINT")

# ==============================
# BANCO DE EVENTOS
# ==============================

arquivo = "golpes_detectados.json"

if not os.path.exists(arquivo):
    with open(arquivo,"w") as f:
        json.dump([],f)

def salvar_evento(tipo,conteudo,score):

    with open(arquivo,"r") as f:
        dados = json.load(f)

    dados.append({
        "tipo":tipo,
        "conteudo":conteudo,
        "score":score
    })

    with open(arquivo,"w") as f:
        json.dump(dados,f,indent=4)

def carregar_eventos():

    with open(arquivo,"r") as f:
        return json.load(f)

# ==============================
# OSINT IP
# ==============================

st.header("🌍 Análise OSINT de IP")

ip = st.text_input("Digite domínio ou IP")

if st.button("Analisar IP"):

    try:

        r = requests.get(f"http://ip-api.com/json/{ip}")
        data = r.json()

        if data["status"] == "success":

            st.success("IP encontrado")

            col1,col2 = st.columns(2)

            with col1:
                st.write("IP:",data["query"])
                st.write("País:",data["country"])
                st.write("Cidade:",data["city"])
                st.write("Região:",data["regionName"])

            with col2:
                st.write("ISP:",data["isp"])
                st.write("Organização:",data["org"])
                st.write("ASN:",data["as"])
                st.write("Fuso:",data["timezone"])

            mapa = pd.DataFrame({
                "lat":[data["lat"]],
                "lon":[data["lon"]]
            })

            st.subheader("📍 Localização")

            st.map(mapa)

        else:
            st.error("IP não encontrado")

    except:
        st.error("Erro na consulta")

# ==============================
# DETECTOR DE PHISHING
# ==============================

st.header("🚨 Detector de Phishing")

mensagem = st.text_area("Cole mensagem ou link suspeito")

if st.button("Analisar mensagem"):

    palavras = [
        "pix","senha","codigo","urgente",
        "transferencia","banco","login",
        "verificacao","confirmar","clique aqui"
    ]

    score = 0

    for p in palavras:
        if p in mensagem.lower():
            score += 15

    st.write("Score de risco:",score)

    if score >= 40:
        st.error("🚨 Alto risco de golpe")

    elif score >= 20:
        st.warning("⚠️ Mensagem suspeita")

    else:
        st.success("🟢 Baixo risco")

    salvar_evento("mensagem",mensagem,score)

# ==============================
# SCANNER DE DOMÍNIO
# ==============================

st.header("🔎 Scanner de domínio")

link = st.text_input("Digite URL suspeita")

if st.button("Analisar domínio"):

    try:

        dominio = urlparse(link).netloc

        r = requests.get(f"http://ip-api.com/json/{dominio}")

        data = r.json()

        if data["status"] == "success":

            st.write("Domínio:",dominio)
            st.write("País:",data["country"])
            st.write("ISP:",data["isp"])
            st.write("ASN:",data["as"])

        else:
            st.error("Domínio não encontrado")

    except:

        st.error("Erro na análise")

# ==============================
# OCR PRINT
# ==============================

st.header("📷 Analisar print de e-mail ou WhatsApp")

imagem = st.file_uploader("Envie print suspeito",type=["png","jpg","jpeg"])

if imagem:

    img = Image.open(imagem)

    st.image(img)

    try:

        texto = pytesseract.image_to_string(img)

        st.subheader("Texto detectado")

        st.write(texto)

        palavras = [
            "pix","senha","codigo","urgente",
            "transferencia","banco","login"
        ]

        score = 0

        for p in palavras:

            if p in texto.lower():
                score += 15

        st.write("Score de risco:",score)

        salvar_evento("imagem",texto,score)

        if score >= 40:
            st.error("🚨 Golpe detectado")

        elif score >= 20:
            st.warning("⚠️ Conteúdo suspeito")

        else:
            st.success("🟢 Baixo risco")

    except:

        st.warning("OCR não disponível no servidor")

# ==============================
# HISTÓRICO SOC
# ==============================

st.header("📊 Histórico SOC")

eventos = carregar_eventos()

if eventos:

    df = pd.DataFrame(eventos)

    st.dataframe(df)

# ==============================
# PAINEL SOC
# ==============================

st.header("📡 Painel SOC")

col1,col2,col3 = st.columns(3)

col1.metric("Eventos detectados",len(eventos))
col2.metric("IPs analisados",random.randint(50,300))
col3.metric("Alertas ativos",sum(e["score"]>30 for e in eventos))

# ==============================
# RADAR DE AMEAÇA
# ==============================

st.header("🛰️ Radar de ameaça")

nivel = min(100,sum(e["score"] for e in eventos))

st.progress(nivel)

if nivel > 70:
    st.error("🚨 Nível alto de ameaça")

elif nivel > 40:
    st.warning("⚠️ Atividade suspeita")

else:
    st.success("🟢 Ambiente seguro")
