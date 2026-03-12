import streamlit as st
import requests
import pandas as pd
import json
import datetime
import io
from PIL import Image
from reportlab.pdfgen import canvas
import folium
from streamlit_folium import st_folium

try:
    import pytesseract
    OCR_OK = True
except:
    OCR_OK = False


st.set_page_config(page_title="Escudo Digital IA", layout="wide")


# 🎨 fundo melhor
st.markdown("""
<style>

.stApp {
background: linear-gradient(135deg,#020617,#071a2f);
color:white;
}

h1,h2,h3 {
color:#00ffa6;
text-shadow:0 0 6px #00ffa6;
}

.stButton>button {
background: linear-gradient(90deg,#00ffa6,#00c2ff);
border-radius:10px;
color:black;
font-weight:bold;
}

</style>
""", unsafe_allow_html=True)


st.title("🛡️ ESCUDO DIGITAL IA")
st.subheader("SOC de monitoramento de golpes e análise OSINT")


# carregar histórico
try:
    with open("historico.json","r") as f:
        historico = json.load(f)
except:
    historico = []


def registrar(tipo,score,detalhe=""):

    evento = {
        "data": str(datetime.datetime.now()),
        "tipo": tipo,
        "score": score,
        "detalhe": detalhe
    }

    historico.append(evento)

    with open("historico.json","w") as f:
        json.dump(historico,f)



# =================
# OSINT IP
# =================

st.header("🌍 Análise OSINT de IP")

ip = st.text_input("Digite domínio ou IP")

if st.button("Analisar IP"):

    try:

        r = requests.get(f"http://ip-api.com/json/{ip}").json()

        st.write("IP:",ip)
        st.write("País:",r.get("country"))
        st.write("Cidade:",r.get("city"))
        st.write("ISP:",r.get("isp"))
        st.write("ASN:",r.get("as"))

        registrar("ip",1,ip)

        lat = r.get("lat")
        lon = r.get("lon")

        if lat and lon:

            st.subheader("🌍 Origem do IP")

            mapa = folium.Map(
                location=[lat,lon],
                zoom_start=4
            )

            folium.Marker(
                [lat,lon],
                tooltip=ip
            ).add_to(mapa)

            st_folium(mapa,width=700,height=500)

    except:
        st.error("Erro na consulta")


# =================
# PHISHING
# =================

st.header("🚨 Detector de Phishing")

msg = st.text_area("Cole mensagem ou link suspeito")

if st.button("Analisar mensagem"):

    palavras = [
        "pix","senha","urgente",
        "banco","login","clique",
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


# =================
# DOMÍNIO
# =================

st.header("🔎 Scanner de domínio")

dominio = st.text_input("Digite URL suspeita")

if st.button("Scanner domínio"):

    try:

        r = requests.get(f"http://ip-api.com/json/{dominio}").json()

        st.write("Domínio:",dominio)
        st.write("País:",r.get("country"))
        st.write("ISP:",r.get("isp"))
        st.write("ASN:",r.get("as"))

        registrar("dominio",1,dominio)

    except:
        st.error("Erro")


# =================
# PRINT OCR
# =================

st.header("📷 Analisar print de e-mail ou WhatsApp")

file = st.file_uploader("Envie print suspeito")

if file:

    image = Image.open(file)

    st.image(image)

    if OCR_OK:

        texto = pytesseract.image_to_string(image)

        st.subheader("Texto detectado")

        st.write(texto)

        registrar("imagem",1,texto[:80])


# =================
# EMAIL
# =================

st.header("📧 Analisar e-mail suspeito")

email = st.text_area("Cole o conteúdo do e-mail")

if st.button("Analisar e-mail"):

    palavras = [
        "senha","urgente",
        "pix","bloqueado",
        "verificar"
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


# =================
# HISTÓRICO
# =================

st.header("📊 Histórico SOC")

if historico:

    df = pd.DataFrame(historico)

    st.dataframe(df)


# =================
# PAINEL
# =================

st.header("📡 Painel SOC")

eventos = len(historico)

suspeitos = len([e for e in historico if e.get("score",0)>=2])

alertas = suspeitos

col1,col2,col3 = st.columns(3)

col1.metric("Eventos detectados",eventos)
col2.metric("Eventos suspeitos",suspeitos)
col3.metric("Alertas ativos",alertas)


# =================
# RADAR
# =================

st.header("🛰️ Radar de ameaça")

if alertas >=5:
    st.error("🚨 Nível alto de ameaça")

elif alertas >=1:
    st.warning("⚠️ Atividade suspeita")

else:
    st.success("🟢 Ambiente seguro")


# =================
# RELATÓRIO
# =================

st.header("📄 Gerar relatório")

if st.button("Gerar relatório PDF"):

    buffer = io.BytesIO()

    c = canvas.Canvas(buffer)

    y = 800

    c.drawString(50,y,"Relatório Escudo Digital IA")

    y -= 40

    for e in historico:

        linha = f"{e.get('data')} | {e.get('tipo')} | score:{e.get('score')}"

        c.drawString(50,y,linha)

        y -= 20

    c.save()

    st.download_button(
        "Baixar relatório",
        buffer.getvalue(),
        "relatorio_soc.pdf"
    )
