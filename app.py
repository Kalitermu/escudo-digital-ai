import streamlit as st
import requests
import pandas as pd
import json
import datetime
import io
import difflib
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
# TEMA AZUL ANIL SUAVE
# =========================

st.markdown("""
<style>

.stApp{
background: linear-gradient(135deg,#e8f1ff,#cfe0ff);
color:#0f172a;
}

h1,h2,h3{
color:#1d4ed8;
}

p,span,label,div{
color:#0f172a !important;
}

input{
background:white !important;
color:black !important;
}

textarea{
background:white !important;
color:black !important;
}

.stButton>button{
background:linear-gradient(90deg,#3b82f6,#2563eb);
border-radius:12px;
color:white;
font-weight:bold;
}

[data-testid="stMetricValue"]{
color:#0f172a !important;
font-size:30px;
}

[data-testid="stMetricLabel"]{
color:#1e40af !important;
}

</style>
""", unsafe_allow_html=True)

st.title("🛡️ ESCUDO DIGITAL IA")
st.subheader("SOC de monitoramento de golpes e análise OSINT")

# =========================
# BASE DE DADOS
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

def salvar(nome,dados):
    with open(nome,"w") as f:
        json.dump(dados,f)

def registrar(tipo,score,detalhe=""):
    evento={
        "data":str(datetime.datetime.now()),
        "tipo":tipo,
        "score":score,
        "detalhe":detalhe
    }
    historico.append(evento)
    salvar("historico.json",historico)

def registrar_ip(ip,lat,lon,pais,isp):
    registro={
        "ip":ip,
        "lat":lat,
        "lon":lon,
        "pais":pais,
        "isp":isp
    }
    mapa_ips.append(registro)
    salvar("mapa_ips.json",mapa_ips)

# =========================
# DETECTOR DOMÍNIO FALSO
# =========================

sites_legitimos=[
"google.com",
"facebook.com",
"instagram.com",
"paypal.com",
"amazon.com",
"bradesco.com.br",
"itau.com.br",
"nubank.com.br"
]

def detectar_dominio(url):

    risco=0

    palavras=["login","secure","verify","update","account"]

    for p in palavras:
        if p in url.lower():
            risco+=1

    for site in sites_legitimos:
        similaridade=difflib.SequenceMatcher(None,url,site).ratio()
        if similaridade>0.6 and url!=site:
            risco+=2

    return risco

# =========================
# OSINT IP
# =========================

st.header("🌍 Análise OSINT de IP")

ip=st.text_input("Digite domínio ou IP")

if st.button("Analisar IP"):

    try:

        r=requests.get(f"http://ip-api.com/json/{ip}").json()

        pais=r.get("country")
        cidade=r.get("city")
        isp=r.get("isp")
        asn=r.get("as")
        lat=r.get("lat")
        lon=r.get("lon")

        st.success("Consulta realizada")

        st.write("IP:",ip)
        st.write("País:",pais)
        st.write("Cidade:",cidade)
        st.write("ISP:",isp)
        st.write("ASN:",asn)

        registrar("ip",1,ip)

        if lat and lon:

            registrar_ip(ip,lat,lon,pais,isp)

            mapa=folium.Map(location=[lat,lon],zoom_start=4)

            folium.Marker(
                [lat,lon],
                popup=f"IP: {ip}<br>País: {pais}<br>ISP: {isp}",
                tooltip="Clique para detalhes"
            ).add_to(mapa)

            st_folium(mapa,width=700,height=450)

    except:
        st.error("Erro na consulta")

# =========================
# RADAR GLOBAL
# =========================

st.header("🌎 Radar global de ameaças")

if mapa_ips:

    mapa_global=folium.Map(location=[0,0],zoom_start=2)

    for item in mapa_ips:

        ip=item.get("ip","?")
        pais=item.get("pais","desconhecido")
        isp=item.get("isp","desconhecido")
        lat=item.get("lat")
        lon=item.get("lon")

        if lat and lon:

            folium.CircleMarker(
                location=[lat,lon],
                radius=6,
                color="red",
                fill=True,
                popup=f"IP: {ip}<br>País: {pais}<br>ISP: {isp}"
            ).add_to(mapa_global)

    st_folium(mapa_global,width=900,height=500)

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
# SCANNER DOMÍNIO
# =========================

st.header("🔎 Scanner de domínio")

dominio=st.text_input("Digite URL suspeita")

if st.button("Analisar domínio"):

    score=detectar_dominio(dominio)

    if score>=3:
        st.error("🚨 Domínio muito suspeito")

    elif score>=1:
        st.warning("⚠️ Domínio suspeito")

    else:
        st.success("🟢 Domínio aparentemente seguro")

    registrar("dominio",score,dominio)

# =========================
# OCR PRINT
# =========================

st.header("📷 Analisar print de golpe")

file=st.file_uploader("Envie print",type=["png","jpg","jpeg"])

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

st.header("📧 Analisar email suspeito")

email=st.text_area("Cole o conteúdo do email")

if st.button("Analisar email"):

    palavras=["senha","urgente","pix","bloqueado"]

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
# RELATÓRIO
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
