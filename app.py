import streamlit as st
import requests
import pandas as pd
import json
import datetime
from PIL import Image
from reportlab.pdfgen import canvas
import io

st.set_page_config(page_title="Escudo Digital IA", layout="wide")

st.title("🛡️ ESCUDO DIGITAL IA")
st.subheader("SOC de monitoramento de golpes e análise OSINT")

# carregar histórico
try:
    with open("historico.json","r") as f:
        historico = json.load(f)
except:
    historico = []

def registrar(tipo,score):
    evento = {
        "data": str(datetime.datetime.now()),
        "tipo": tipo,
        "score": score
    }
    historico.append(evento)
    with open("historico.json","w") as f:
        json.dump(historico,f)

# -----------------------------
# OSINT IP
# -----------------------------

st.header("🌍 Análise OSINT de IP")

ip = st.text_input("Digite domínio ou IP")

if st.button("Analisar IP"):

    try:

        r = requests.get(f"http://ip-api.com/json/{ip}").json()

        st.write("IP:",ip)
        st.write("País:",r.get("country"))
        st.write("Cidade:",r.get("city"))
        st.write("ISP:",r.get("isp"))

        registrar("ip",1)

    except:
        st.error("Erro na consulta")

# -----------------------------
# phishing
# -----------------------------

st.header("🚨 Detector de Phishing")

msg = st.text_area("Cole mensagem ou link suspeito")

if st.button("Analisar mensagem"):

    score = 0

    palavras = [
        "urgente",
        "senha",
        "pix",
        "clique",
        "banco",
        "atualizar",
        "ganhou"
    ]

    for p in palavras:

        if p in msg.lower():
            score += 1

    if score >= 2:
        st.error("🚨 Possível phishing")

    else:
        st.success("🟢 Baixo risco")

    registrar("mensagem",score)

# -----------------------------
# scanner dominio
# -----------------------------

st.header("🔎 Scanner de domínio")

dominio = st.text_input("Digite URL suspeita")

if st.button("Scanner domínio"):

    try:

        r = requests.get(f"http://ip-api.com/json/{dominio}").json()

        st.write("Domínio:",dominio)
        st.write("País:",r.get("country"))
        st.write("ISP:",r.get("isp"))
        st.write("ASN:",r.get("as"))

        registrar("dominio",1)

    except:

        st.error("Erro")

# -----------------------------
# analisar print
# -----------------------------

st.header("📷 Analisar print de e-mail ou WhatsApp")

file = st.file_uploader("Envie print suspeito")

if file:

    image = Image.open(file)

    st.image(image)

    st.write("Imagem recebida")

    registrar("imagem",1)

# -----------------------------
# email
# -----------------------------

st.header("📧 Analisar e-mail suspeito")

email = st.text_area("Cole o conteúdo do e-mail")

if st.button("Analisar e-mail"):

    score = 0

    palavras = [
        "senha",
        "urgente",
        "bloqueado",
        "pix",
        "verificar"
    ]

    for p in palavras:

        if p in email.lower():
            score += 1

    if score >= 2:
        st.error("🚨 Email suspeito")

    else:
        st.success("🟢 Baixo risco")

    registrar("email",score)

# -----------------------------
# histórico
# -----------------------------

st.header("📊 Histórico SOC")

if historico:

    df = pd.DataFrame(historico)

    st.dataframe(df)

    st.header("📈 Gráfico de eventos")

    st.bar_chart(df["tipo"].value_counts())

# -----------------------------
# painel SOC
# -----------------------------

st.header("📡 Painel SOC")

eventos = len(historico)

suspeitos = len([e for e in historico if e.get("score",0) >= 2])

alertas = suspeitos

col1,col2,col3 = st.columns(3)

col1.metric("Eventos detectados",eventos)
col2.metric("Eventos suspeitos",suspeitos)
col3.metric("Alertas ativos",alertas)

# -----------------------------
# radar
# -----------------------------

st.header("🛰️ Radar de ameaça")

if alertas >= 3:
    st.error("🚨 Nível alto de ameaça")

elif alertas >= 1:
    st.warning("⚠️ Atividade suspeita")

else:
    st.success("🟢 Ambiente seguro")

# -----------------------------
# relatório PDF
# -----------------------------

st.header("📄 Gerar relatório")

if st.button("Gerar relatório PDF"):

    buffer = io.BytesIO()

    c = canvas.Canvas(buffer)

    y = 800

    c.drawString(50,y,"Relatório Escudo Digital")
    y -= 40

    for e in historico:

        linha = f"{e.get('data','?')} | {e.get('tipo','?')} | score:{e.get('score','0')}"

        c.drawString(50,y,linha)

        y -= 20

    c.save()

    st.download_button(
        "Baixar relatório",
        buffer.getvalue(),
        "relatorio_soc.pdf"
    )
