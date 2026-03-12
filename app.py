import streamlit as st
import requests
import pandas as pd
import json
import os
import re
from datetime import datetime
from PIL import Image
import pytesseract
from urllib.parse import urlparse
from reportlab.pdfgen import canvas
import tempfile

st.set_page_config(page_title="Escudo Digital IA", layout="wide")

st.title("🛡️ ESCUDO DIGITAL IA")
st.write("SOC de monitoramento de golpes e análise OSINT")

ARQUIVO = "golpes_detectados.json"

if not os.path.exists(ARQUIVO):
    with open(ARQUIVO,"w") as f:
        json.dump([],f)

def salvar_evento(tipo,conteudo,score):

    with open(ARQUIVO,"r") as f:
        dados = json.load(f)

    dados.append({
        "data":datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "tipo":tipo,
        "conteudo":conteudo,
        "score":score
    })

    with open(ARQUIVO,"w") as f:
        json.dump(dados,f,indent=4)

def carregar():

    with open(ARQUIVO) as f:
        return json.load(f)

eventos = carregar()

# =====================================
# OSINT IP
# =====================================

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

            with col2:
                st.write("ISP:",data["isp"])
                st.write("Organização:",data["org"])
                st.write("ASN:",data["as"])

            mapa = pd.DataFrame({
                "lat":[data["lat"]],
                "lon":[data["lon"]]
            })

            st.map(mapa)

            salvar_evento("ip",data["query"],10)

        else:

            st.error("IP não encontrado")

    except:

        st.error("Erro na consulta")

# =====================================
# PHISHING
# =====================================

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
        st.error("🚨 Alto risco")

    elif score >= 20:
        st.warning("⚠️ Suspeito")

    else:
        st.success("🟢 Seguro")

    salvar_evento("mensagem",mensagem,score)

# =====================================
# DETECTOR DE LINKS
# =====================================

st.header("🔗 Detector automático de links")

links = re.findall(r'https?://\S+', mensagem)

if links:

    for link in links:

        dominio = urlparse(link).netloc

        st.write("Link detectado:",dominio)

        try:

            r = requests.get(f"http://ip-api.com/json/{dominio}")

            data = r.json()

            if data["status"] == "success":

                st.write("País:",data["country"])
                st.write("ISP:",data["isp"])

        except:

            st.warning("Não foi possível analisar o domínio")

# =====================================
# SCANNER DOMINIO
# =====================================

st.header("🔎 Scanner de domínio")

url = st.text_input("Digite URL suspeita")

if st.button("Analisar domínio"):

    dominio = urlparse(url).netloc

    r = requests.get(f"http://ip-api.com/json/{dominio}")

    data = r.json()

    if data["status"] == "success":

        st.write("Domínio:",dominio)
        st.write("País:",data["country"])
        st.write("ISP:",data["isp"])
        st.write("ASN:",data["as"])

        salvar_evento("dominio",dominio,15)

# =====================================
# PRINT
# =====================================

st.header("📷 Analisar print")

img = st.file_uploader("Envie print suspeito",type=["png","jpg","jpeg"])

if img:

    imagem = Image.open(img)

    st.image(imagem)

    try:

        texto = pytesseract.image_to_string(imagem)

        st.write("Texto detectado")

        st.write(texto)

        score = 0

        if "pix" in texto.lower():

            score += 20

        salvar_evento("imagem",texto,score)

    except:

        st.warning("OCR não disponível")

# =====================================
# EMAIL
# =====================================

st.header("📧 Analisar e-mail suspeito")

email = st.text_area("Cole o e-mail")

if st.button("Analisar e-mail"):

    score = 0

    if "senha" in email.lower():

        score += 20

    if "pix" in email.lower():

        score += 20

    st.write("Score:",score)

    salvar_evento("email",email,score)

# =====================================
# HISTORICO
# =====================================

st.header("📊 Histórico SOC")

eventos = carregar()

if eventos:

    df = pd.DataFrame(eventos)

    st.dataframe(df)

# =====================================
# GRAFICO
# =====================================

st.header("📈 Gráfico de eventos")

if eventos:

    df = pd.DataFrame(eventos)

    st.bar_chart(df["tipo"].value_counts())

# =====================================
# MAPA DE ATAQUES
# =====================================

st.header("🌎 Mapa de análises")

lat = []
lon = []

for e in eventos:

    if e["tipo"] == "ip":

        try:

            r = requests.get(f"http://ip-api.com/json/{e['conteudo']}")

            d = r.json()

            if d["status"] == "success":

                lat.append(d["lat"])
                lon.append(d["lon"])

        except:

            pass

if lat:

    mapa = pd.DataFrame({"lat":lat,"lon":lon})

    st.map(mapa)

# =====================================
# PAINEL SOC
# =====================================

st.header("📡 Painel SOC")

col1,col2,col3 = st.columns(3)

col1.metric("Eventos detectados",len(eventos))

col2.metric("Suspeitos",sum(e["score"]>20 for e in eventos))

col3.metric("Alertas ativos",sum(e["score"]>40 for e in eventos))

# =====================================
# RADAR
# =====================================

st.header("🛰️ Radar de ameaça")

nivel = min(100,sum(e["score"] for e in eventos))

st.progress(nivel)

if nivel > 70:

    st.error("🚨 Nível alto de ameaça")

elif nivel > 40:

    st.warning("⚠️ Atividade suspeita")

else:

    st.success("🟢 Ambiente seguro")

# =====================================
# RELATORIO PDF
# =====================================

st.header("📁 Exportar relatório")

if st.button("Gerar relatório SOC"):

    with tempfile.NamedTemporaryFile(delete=False,suffix=".pdf") as tmp:

        c = canvas.Canvas(tmp.name)

        c.drawString(50,800,"ESCUDO DIGITAL IA - Relatório SOC")

        y = 760

        for e in eventos[-10:]:

            c.drawString(50,y,f"{e['data']} | {e['tipo']} | score:{e['score']}")

            y -= 20

        c.save()

        with open(tmp.name,"rb") as f:

            st.download_button("Baixar PDF",f,file_name="relatorio_soc.pdf")
