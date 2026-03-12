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
    OCR_OK=True
except:
    OCR_OK=False

st.set_page_config(page_title="Escudo Digital IA",layout="wide")

# =========================
# ESTILO VISUAL
# =========================

st.markdown("""
<style>

.stApp{
background: linear-gradient(135deg,#020617,#071a2f);
color:white;
}

p,span,label,div{
color:white !important;
}

h1,h2,h3{
color:#00ffa6;
text-shadow:0 0 6px #00ffa6;
}

.stButton>button{
background:linear-gradient(90deg,#00ffa6,#00c2ff);
border-radius:10px;
color:black;
font-weight:bold;
}

[data-testid="stMetricValue"]{
color:white !important;
font-size:28px;
}

[data-testid="stMetricLabel"]{
color:#a7f3d0 !important;
}

</style>
""",unsafe_allow_html=True)

st.title("🛡️ ESCUDO DIGITAL IA")
st.subheader("SOC de monitoramento de golpes e análise OSINT")

# =========================
# HISTÓRICO
# =========================

try:
    with open("historico.json","r") as f:
        historico=json.load(f)
except:
    historico=[]

try:
    with open("mapa_ips.json","r") as f:
        mapa_ips=json.load(f)
except:
    mapa_ips=[]

def registrar(tipo,score,detalhe=""):

    evento={
        "data":str(datetime.datetime.now()),
        "tipo":tipo,
        "score":score,
        "detalhe":detalhe
    }

    historico.append(evento)

    with open("historico.json","w") as f:
        json.dump(historico,f)

def registrar_ip(ip,lat,lon):

    mapa_ips.append({
        "ip":ip,
        "lat":lat,
        "lon":lon
    })

    with open("mapa_ips.json","w") as f:
        json.dump(mapa_ips,f)

# =========================
# OSINT IP
# =========================

st.header("🌍 Análise OSINT de IP")

ip=st.text_input("Digite domínio ou IP")

if st.button("Analisar IP"):

    try:

        r=requests.get(f"http://ip-api.com/json/{ip}").json()

        st.write("IP:",ip)
        st.write("País:",r.get("country"))
        st.write("Cidade:",r.get("city"))
        st.write("ISP:",r.get("isp"))
        st.write("ASN:",r.get("as"))

        registrar("ip",1,ip)

        lat=r.get("lat")
        lon=r.get("lon")

        if lat and lon:

            registrar_ip(ip,lat,lon)

            mapa=folium.Map(location=[lat,lon],zoom_start=4)

            folium.Marker([lat,lon],tooltip=ip).add_to(mapa)

            st.subheader("🌍 Origem do IP")

            st_folium(mapa,width=700,height=450)

    except:
        st.error("Erro na consulta")

# =========================
# MAPA GLOBAL
# =========================

st.header("🌎 Radar global de ameaças")

if mapa_ips:

    mapa_global=folium.Map(location=[0,0],zoom_start=2)

    for ip in mapa_ips:

        folium.CircleMarker(
            location=[ip["lat"],ip["lon"]],
            radius=5,
            color="red",
            fill=True
        ).add_to(mapa_global)

    st_folium(mapa_global,width=900,height=450)

# =========================
# DETECTOR PHISHING
# =========================

st.header("🚨 Detector de Phishing")

msg=st.text_area("Cole mensagem ou link suspeito")

if st.button("Analisar mensagem"):

    palavras=[
        "pix","senha","urgente","banco",
        "login","clique","transferência",
        "verificação","código"
    ]

    score=0

    for p in palavras:
        if p in msg.lower():
            score+=1

    if score>=4:
        st.error("🚨 Alto risco de golpe")

    elif score>=2:
        st.warning("⚠️ Mensagem suspeita")

    else:
        st.success("🟢 Baixo risco")

    registrar("mensagem",score,msg[:100])

# =========================
# DOMÍNIO
# =========================

st.header("🔎 Scanner de domínio")

dominio=st.text_input("Digite URL suspeita")

if st.button("Scanner domínio"):

    try:

        r=requests.get(f"http://ip-api.com/json/{dominio}").json()

        st.write("País:",r.get("country"))
        st.write("ISP:",r.get("isp"))
        st.write("ASN:",r.get("as"))

        registrar("dominio",1,dominio)

    except:
        st.error("Erro")

# =========================
# OCR PRINT
# =========================

st.header("📷 Analisar print de e-mail ou WhatsApp")

file=st.file_uploader("Envie print suspeito")

if file:

    image=Image.open(file)

    st.image(image)

    if OCR_OK:

        texto=pytesseract.image_to_string(image)

        st.subheader("Texto detectado")

        st.write(texto)

        registrar("imagem",1,texto[:100])

# =========================
# EMAIL
# =========================

st.header("📧 Analisar e-mail suspeito")

email=st.text_area("Cole o conteúdo do e-mail")

if st.button("Analisar e-mail"):

    palavras=["senha","urgente","pix","bloqueado","verificar","clique aqui"]

    score=0

    for p in palavras:
        if p in email.lower():
            score+=1

    if score>=2:
        st.error("🚨 Email suspeito")
    else:
        st.success("🟢 Baixo risco")

    registrar("email",score,email[:100])

# =========================
# HISTÓRICO
# =========================

st.header("📊 Histórico SOC")

if historico:

    df=pd.DataFrame(historico)

    st.dataframe(df)

# =========================
# PAINEL SOC
# =========================

st.header("📡 Painel SOC")

eventos=len(historico)

suspeitos=len([e for e in historico if e.get("score",0)>=2])

alertas=suspeitos

c1,c2,c3=st.columns(3)

c1.metric("Eventos detectados",eventos)
c2.metric("Eventos suspeitos",suspeitos)
c3.metric("Alertas ativos",alertas)

# =========================
# RADAR
# =========================

st.header("🛰️ Radar de ameaça")

if alertas>=5:
    st.error("🚨 Nível alto de ameaça")

elif alertas>=1:
    st.warning("⚠️ Atividade suspeita")

else:
    st.success("🟢 Ambiente seguro")

# =========================
# RELATÓRIO PDF
# =========================

st.header("📄 Gerar relatório")

if st.button("Gerar relatório PDF"):

    buffer=io.BytesIO()

    c=canvas.Canvas(buffer)

    y=800

    c.drawString(50,y,"Relatório Escudo Digital IA")

    y-=40

    for e in historico:

        linha=f"{e.get('data')} | {e.get('tipo')} | score:{e.get('score')}"

        c.drawString(50,y,linha)

        y-=20

    c.save()

    st.download_button(
        "Baixar relatório",
        buffer.getvalue(),
        "relatorio_soc.pdf"
    )
