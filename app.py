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
    OCR_OK = True
except:
    OCR_OK = False

st.set_page_config(page_title="Escudo Digital IA", layout="wide")

# =========================
# TEMA VISUAL
# =========================

st.markdown("""
<style>
.stApp{
background: linear-gradient(135deg,#eef4ff,#d9e8ff);
color:#0f172a;
}
h1,h2,h3{
color:#1d4ed8;
}
input, textarea{
background:white !important;
color:black !important;
border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ ESCUDO DIGITAL IA")
st.subheader("SOC de monitoramento de golpes e análise OSINT")

# =========================
# ARQUIVOS
# =========================

HIST_ARQ = "historico.json"
MAPA_ARQ = "mapa_ips.json"

def carregar(nome):
    try:
        with open(nome,"r") as f:
            return json.load(f)
    except:
        return []

def salvar(nome,dados):
    with open(nome,"w") as f:
        json.dump(dados,f)

historico = carregar(HIST_ARQ)
mapa_ips = carregar(MAPA_ARQ)

def registrar(tipo,score,detalhe):
    evento={
    "data":str(datetime.datetime.now()),
    "tipo":tipo,
    "score":score,
    "detalhe":detalhe
    }
    historico.append(evento)
    salvar(HIST_ARQ,historico)

# =========================
# DETECÇÃO
# =========================

palavras_golpe = [
"empréstimo","emprestimo","pix","senha","login",
"pré-aprovado","pre-aprovado","urgente","clique",
"crédito","credito","taxa"
]

def detectar_golpe(texto):

    texto=texto.lower()
    score=0
    sinais=[]

    for p in palavras_golpe:
        if p in texto:
            score+=1
            sinais.append(p)

    return score,sinais

# =========================
# DOMÍNIO
# =========================

sites_legitimos=[
"google.com",
"facebook.com",
"paypal.com",
"amazon.com",
"gov.br"
]

def detectar_dominio(url):

    url=url.lower().replace("https://","").replace("http://","")
    score=0
    motivos=[]

    for site in sites_legitimos:

        similaridade=difflib.SequenceMatcher(None,url,site).ratio()

        if similaridade>0.60 and url!=site:
            score+=2
            motivos.append(f"parecido com {site}")

    return score,motivos

# =========================
# OSINT IP
# =========================

st.header("🌍 Análise OSINT de IP")

ip=st.text_input("Digite domínio ou IP")

if st.button("Analisar IP"):

    try:

        r=requests.get(f"http://ip-api.com/json/{ip}").json()

        if r["status"]=="success":

            st.success("Consulta realizada")

            st.write("IP:",ip)
            st.write("País:",r["country"])
            st.write("Cidade:",r["city"])
            st.write("ISP:",r["isp"])

            registrar("ip",1,ip)

            lat=r["lat"]
            lon=r["lon"]

            mapa=folium.Map(location=[lat,lon],zoom_start=4)

            folium.Marker(
            [lat,lon],
            popup=f"{ip} - {r['country']}"
            ).add_to(mapa)

            st_folium(mapa,width=700,height=400)

    except:

        st.error("Erro na consulta")

# =========================
# RADAR GLOBAL
# =========================

st.header("🌎 Radar global de ameaças")

if mapa_ips:

    mapa=folium.Map(location=[0,0],zoom_start=2)

    for item in mapa_ips:

        folium.CircleMarker(
        [item["lat"],item["lon"]],
        radius=5,
        color="red",
        fill=True
        ).add_to(mapa)

    st_folium(mapa,width=900,height=500)

# =========================
# DETECTOR DE PHISHING
# =========================

st.header("🚨 Detector de Phishing")

msg=st.text_area("Cole mensagem suspeita")

if st.button("Analisar mensagem"):

    score,sinais=detectar_golpe(msg)

    if score>=4:
        st.error("🚨 Alto risco de golpe")
    elif score>=2:
        st.warning("⚠ Conteúdo suspeito")
    else:
        st.success("🟢 Baixo risco")

    st.write("Score:",score)

    if sinais:
        st.write("Sinais:",",".join(sinais))

    registrar("mensagem",score,msg[:120])

# =========================
# DOMÍNIO
# =========================

st.header("🔎 Scanner de domínio")

dom=st.text_input("Digite URL suspeita")

if st.button("Analisar domínio"):

    score,motivos=detectar_dominio(dom)

    if score>=2:
        st.warning("⚠ Domínio suspeito")
    else:
        st.success("🟢 Domínio seguro")

    st.write("Score:",score)

    if motivos:
        st.write("Motivos:",",".join(motivos))

    registrar("dominio",score,dom)

# =========================
# OCR PRINT
# =========================

st.header("📷 Analisar print de golpe")

arquivo=st.file_uploader("Envie print",type=["png","jpg","jpeg"])

if arquivo:

    img=Image.open(arquivo)
    st.image(img)

    if OCR_OK:

        texto=pytesseract.image_to_string(img)

        st.write("Texto detectado:")
        st.write(texto)

        score,sinais=detectar_golpe(texto)

        if score>=4:
            st.error("🚨 Possível golpe detectado")
        elif score>=2:
            st.warning("⚠ Conteúdo suspeito")

        registrar("imagem",score,texto[:120])

# =========================
# EMAIL
# =========================

st.header("📧 Analisar email suspeito")

email=st.text_area("Cole o email")

if st.button("Analisar email"):

    score,sinais=detectar_golpe(email)

    if score>=4:
        st.error("🚨 Email suspeito")
    elif score>=2:
        st.warning("⚠ Email suspeito")

    registrar("email",score,email[:120])

# =========================
# HISTÓRICO
# =========================

st.header("📊 Histórico SOC")

if historico:

    df=pd.DataFrame(historico)
    st.dataframe(df)

# =========================
# PAINEL
# =========================

st.header("📡 Painel SOC")

eventos=len(historico)

suspeitos=len([e for e in historico if e["score"]>=2])

alertas=len([e for e in historico if e["score"]>=4])

c1,c2,c3=st.columns(3)

c1.metric("Eventos detectados",eventos)
c2.metric("Eventos suspeitos",suspeitos)
c3.metric("Alertas ativos",alertas)

# =========================
# CHAT DO ESCUDO
# =========================

st.header("🤖 Chat do Escudo")

pergunta=st.text_input("Pergunte algo ou peça análise")

def chat(msg):

    msg=msg.lower()

    if "ip" in msg:

        partes=msg.split()

        for p in partes:

            if "." in p:

                try:

                    r=requests.get(f"http://ip-api.com/json/{p}").json()

                    return f"""
🌍 IP analisado

IP: {p}
País: {r['country']}
Cidade: {r['city']}
ISP: {r['isp']}
"""

                except:

                    return "Erro ao analisar IP"

    if "link" in msg or "site" in msg:

        partes=msg.split()

        for p in partes:

            if "." in p:

                score,motivos=detectar_dominio(p)

                return f"""
🔎 Análise de site

Domínio: {p}

Score: {score}

Motivos: {",".join(motivos)}
"""

    if "golpe" in msg or "mensagem" in msg:

        score,sinais=detectar_golpe(msg)

        return f"""
🚨 Possível golpe

Score: {score}

Sinais: {",".join(sinais)}
"""

    return """
🤖 Posso ajudar com:

• analisar IP
• verificar links
• detectar golpes

Exemplo:

analise ip 8.8.8.8
verificar site google-secure-login.com
isso é golpe?
"""

if pergunta:

    resposta=chat(pergunta)

    st.write(resposta)

# =========================
# RELATÓRIO PDF
# =========================

st.header("📄 Gerar relatório")

if st.button("Gerar PDF"):

    buffer=io.BytesIO()
    c=canvas.Canvas(buffer)

    y=800

    c.drawString(50,y,"Relatório Escudo Digital IA")
    y-=40

    for e in historico:

        linha=f"{e['data']} | {e['tipo']} | score:{e['score']}"
        c.drawString(50,y,linha)

        y-=20

    c.save()

    st.download_button(
    "Baixar relatório",
    buffer.getvalue(),
    "relatorio_soc.pdf"
    )
