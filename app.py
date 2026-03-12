import streamlit as st
import requests
import pandas as pd
import json
import datetime
import io
from PIL import Image

# opcional: OCR
try:
    import pytesseract
    OCR_OK = True
except:
    OCR_OK = False

# opcional: mapa
try:
    import folium
    from streamlit_folium import st_folium
    MAP_OK = True
except:
    MAP_OK = False

from reportlab.pdfgen import canvas

st.set_page_config(page_title="Escudo Digital IA", layout="wide")

st.title("🛡️ ESCUDO DIGITAL IA")
st.subheader("SOC de monitoramento de golpes e análise OSINT")

# ======================
# carregar banco SOC
# ======================

try:
    with open("historico.json","r") as f:
        historico = json.load(f)
except:
    historico = []

def registrar(tipo, score, detalhe=""):
    evento = {
        "data": str(datetime.datetime.now()),
        "tipo": tipo,
        "score": score,
        "detalhe": detalhe
    }
    historico.append(evento)
    with open("historico.json","w") as f:
        json.dump(historico,f)

# ======================
# Threat Score
# ======================

def threat_score(score):
    return min(score * 20, 100)

# ======================
# OSINT IP
# ======================

st.header("🌍 Análise OSINT de IP")

ip = st.text_input("Digite domínio ou IP")

if st.button("Analisar IP"):

    try:

        r = requests.get(f"http://ip-api.com/json/{ip}").json()

        st.write("IP:", ip)
        st.write("País:", r.get("country"))
        st.write("Cidade:", r.get("city"))
        st.write("ISP:", r.get("isp"))
        st.write("ASN:", r.get("as"))

        registrar("ip",1,ip)

        if MAP_OK and r.get("lat"):
            mapa = folium.Map(location=[r["lat"], r["lon"]], zoom_start=4)
            folium.Marker([r["lat"], r["lon"]]).add_to(mapa)
            st.subheader("🗺️ Origem do IP")
            st_folium(mapa)

    except:
        st.error("Erro na consulta")

# ======================
# Detector de phishing
# ======================

st.header("🚨 Detector de Phishing")

msg = st.text_area("Cole mensagem ou link suspeito")

if st.button("Analisar mensagem"):

    palavras = [
        "pix","urgente","senha","banco",
        "clique","verificar","login",
        "transferência","código"
    ]

    score = 0

    for p in palavras:
        if p in msg.lower():
            score += 1

    if score >= 3:
        st.error("🚨 Alto risco de golpe")

    elif score >= 1:
        st.warning("⚠️ Mensagem suspeita")

    else:
        st.success("🟢 Baixo risco")

    registrar("mensagem",score,msg[:80])

# ======================
# Scanner domínio
# ======================

st.header("🔎 Scanner de domínio")

dominio = st.text_input("Digite URL suspeita")

if st.button("Scanner domínio"):

    try:

        r = requests.get(f"http://ip-api.com/json/{dominio}").json()

        st.write("Domínio:", dominio)
        st.write("País:", r.get("country"))
        st.write("ISP:", r.get("isp"))
        st.write("ASN:", r.get("as"))

        registrar("dominio",1,dominio)

    except:
        st.error("Erro")

# ======================
# OCR de print
# ======================

st.header("📷 Analisar print de e-mail ou WhatsApp")

file = st.file_uploader("Envie print suspeito")

if file:

    image = Image.open(file)
    st.image(image)

    texto_extraido = ""

    if OCR_OK:
        try:
            texto_extraido = pytesseract.image_to_string(image)
            st.subheader("Texto detectado")
            st.write(texto_extraido)

            registrar("imagem",1,texto_extraido[:80])
        except:
            st.warning("OCR não disponível")

# ======================
# Análise de e-mail
# ======================

st.header("📧 Analisar e-mail suspeito")

email = st.text_area("Cole o conteúdo do e-mail")

if st.button("Analisar e-mail"):

    palavras = [
        "senha","urgente","bloqueado",
        "pix","verificar","login"
    ]

    score = 0

    for p in palavras:
        if p in email.lower():
            score += 1

    if score >= 2:
        st.error("🚨 Email suspeito")

    else:
        st.success("🟢 Baixo risco")

    registrar("email",score,email[:80])

# ======================
# Histórico SOC
# ======================

st.header("📊 Histórico SOC")

if historico:

    df = pd.DataFrame(historico)

    st.dataframe(df)

    st.subheader("📈 Gráfico de eventos")

    st.bar_chart(df["tipo"].value_counts())

# ======================
# Painel SOC
# ======================

st.header("📡 Painel SOC")

eventos = len(historico)

suspeitos = len([e for e in historico if e.get("score",0) >= 2])

alertas = suspeitos

col1,col2,col3 = st.columns(3)

col1.metric("Eventos detectados", eventos)
col2.metric("Eventos suspeitos", suspeitos)
col3.metric("Alertas ativos", alertas)

# ======================
# Radar de ameaça
# ======================

st.header("🛰️ Radar de ameaça")

if alertas >= 5:
    st.error("🚨 Nível alto de ameaça")

elif alertas >= 1:
    st.warning("⚠️ Atividade suspeita")

else:
    st.success("🟢 Ambiente seguro")

# ======================
# Relatório PDF
# ======================

st.header("📄 Gerar relatório")

if st.button("Gerar relatório PDF"):

    buffer = io.BytesIO()

    c = canvas.Canvas(buffer)

    y = 800

    c.drawString(50,y,"Relatório Escudo Digital IA")
    y -= 40

    for e in historico:

        linha = f"{e.get('data','?')} | {e.get('tipo','?')} | score:{e.get('score','0')}"

        c.drawString(50,y,linha)

        y -= 20

    c.save()

    st.download_button(
        "⬇️ Baixar relatório",
        buffer.getvalue(),
        "relatorio_soc.pdf"
    )
