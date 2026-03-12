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
# TEMA MAIS SUAVE
# =========================

st.markdown("""
<style>
.stApp{
    background: linear-gradient(135deg,#eef6ff,#dbeafe);
    color:#0f172a;
}
h1,h2,h3{
    color:#0284c7;
}
p,span,label,div{
    color:#0f172a !important;
}
input{
    background:white !important;
    color:black !important;
    border-radius:8px !important;
}
textarea{
    background:white !important;
    color:black !important;
}
.stButton>button{
    background:linear-gradient(90deg,#38bdf8,#0ea5e9);
    border-radius:12px;
    color:white;
    font-weight:bold;
    border:none;
}
[data-testid="stMetricValue"]{
    color:#0f172a !important;
    font-size:30px;
}
[data-testid="stMetricLabel"]{
    color:#0369a1 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ ESCUDO DIGITAL IA")
st.subheader("SOC de monitoramento de golpes e análise OSINT")

# =========================
# BASES
# =========================

try:
    with open("historico.json", "r", encoding="utf-8") as f:
        historico = json.load(f)
except:
    historico = []

try:
    with open("mapa_ips.json", "r", encoding="utf-8") as f:
        mapa_ips = json.load(f)
except:
    mapa_ips = []

sites_legitimos = [
    "google.com",
    "facebook.com",
    "instagram.com",
    "paypal.com",
    "amazon.com",
    "bradesco.com.br",
    "itau.com.br",
    "nubank.com.br",
    "mercadolivre.com.br",
    "gov.br"
]

palavras_phishing = [
    "login",
    "secure",
    "verify",
    "update",
    "account",
    "confirm",
    "senha",
    "pix",
    "urgente",
    "banco",
    "clique aqui",
    "verificação",
    "código",
    "bloqueado"
]

def salvar_json(nome_arquivo, dados):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def registrar(tipo, score, detalhe=""):
    evento = {
        "data": str(datetime.datetime.now()),
        "tipo": tipo,
        "score": score,
        "detalhe": detalhe
    }
    historico.append(evento)
    salvar_json("historico.json", historico)

def registrar_ip(ip, lat, lon, pais, isp):
    registro = {
        "ip": ip,
        "lat": lat,
        "lon": lon,
        "pais": pais,
        "isp": isp
    }
    mapa_ips.append(registro)
    salvar_json("mapa_ips.json", mapa_ips)

def detectar_dominio_falso(url):
    risco = 0
    url = url.lower().strip()

    for p in palavras_phishing:
        if p in url:
            risco += 1

    for site in sites_legitimos:
        similaridade = difflib.SequenceMatcher(None, url, site).ratio()
        if similaridade > 0.60 and url != site:
            risco += 2

    return risco

def score_texto(texto):
    score = 0
    texto = texto.lower()

    chaves = [
        "pix", "senha", "urgente", "banco", "login",
        "clique", "transferência", "verificação",
        "código", "bloqueado", "confirme"
    ]

    for p in chaves:
        if p in texto:
            score += 1

    return score

# =========================
# OSINT IP
# =========================

st.header("🌍 Análise OSINT de IP")

ip = st.text_input("Digite domínio ou IP")

if st.button("Analisar IP"):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=10).json()

        pais = r.get("country")
        cidade = r.get("city")
        isp = r.get("isp")
        asn = r.get("as")
        lat = r.get("lat")
        lon = r.get("lon")

        if r.get("status") == "success":
            st.success("Consulta realizada")
            c1, c2 = st.columns(2)

            with c1:
                st.write("**IP:**", ip)
                st.write("**País:**", pais)
                st.write("**Cidade:**", cidade)

            with c2:
                st.write("**ISP:**", isp)
                st.write("**ASN:**", asn)
                st.write("**Organização:**", r.get("org"))

            registrar("ip", 1, ip)

            if lat and lon:
                registrar_ip(ip, lat, lon, pais, isp)

                st.subheader("🌍 Origem do IP")

                mapa = folium.Map(location=[lat, lon], zoom_start=4)
                folium.Marker(
                    [lat, lon],
                    popup=f"IP: {ip}<br>País: {pais}<br>ISP: {isp}",
                    tooltip="Clique para ver detalhes"
                ).add_to(mapa)

                st_folium(mapa, width=700, height=450)
        else:
            st.error("Não foi possível localizar o IP")

    except:
        st.error("Erro na consulta")

# =========================
# RADAR GLOBAL
# =========================

st.header("🌎 Radar global de ameaças")

if mapa_ips:
    mapa_global = folium.Map(location=[0, 0], zoom_start=2)

    for item in mapa_ips:
        folium.CircleMarker(
            location=[item["lat"], item["lon"]],
            radius=6,
            color="red",
            fill=True,
            popup=f"IP: {item['ip']}<br>País: {item['pais']}<br>ISP: {item['isp']}"
        ).add_to(mapa_global)

    st_folium(mapa_global, width=900, height=500)

# =========================
# PHISHING
# =========================

st.header("🚨 Detector de Phishing")

msg = st.text_area("Cole mensagem ou link suspeito")

if st.button("Analisar mensagem"):
    score = score_texto(msg)

    if score >= 4:
        st.error("🚨 Alto risco de golpe")
    elif score >= 2:
        st.warning("⚠️ Mensagem suspeita")
    else:
        st.success("🟢 Baixo risco")

    st.write("**Score:**", score)
    registrar("mensagem", score, msg[:150])

# =========================
# DOMÍNIO
# =========================

st.header("🔎 Scanner de domínio")

dominio = st.text_input("Digite URL suspeita")

if st.button("Scanner domínio"):
    try:
        r = requests.get(f"http://ip-api.com/json/{dominio}", timeout=10).json()

        st.write("**Domínio:**", dominio)
        st.write("**País:**", r.get("country"))
        st.write("**ISP:**", r.get("isp"))
        st.write("**ASN:**", r.get("as"))

        score_dom = detectar_dominio_falso(dominio)

        if score_dom >= 3:
            st.error("🚨 Domínio muito suspeito / parecido com site legítimo")
        elif score_dom >= 1:
            st.warning("⚠️ Domínio suspeito")
        else:
            st.success("🟢 Domínio aparentemente seguro")

        st.write("**Score do domínio:**", score_dom)

        registrar("dominio", score_dom if score_dom > 0 else 1, dominio)

    except:
        st.error("Erro")

# =========================
# PRINT
# =========================

st.header("📷 Analisar print de e-mail ou WhatsApp")

file = st.file_uploader("Envie print suspeito", type=["png", "jpg", "jpeg"])

if file:
    image = Image.open(file)
    st.image(image)

    if OCR_OK:
        try:
            texto = pytesseract.image_to_string(image)

            st.subheader("Texto detectado")
            st.write(texto)

            score = score_texto(texto)

            if score >= 4:
                st.error("🚨 Possível golpe detectado")
            elif score >= 2:
                st.warning("⚠️ Conteúdo suspeito")
            else:
                st.success("🟢 Baixo risco")

            st.write("**Score:**", score)
            registrar("imagem", score if score > 0 else 1, texto[:150])

        except:
            st.warning("OCR não disponível")
    else:
        st.warning("OCR não disponível no servidor")

# =========================
# EMAIL
# =========================

st.header("📧 Analisar e-mail suspeito")

email = st.text_area("Cole o conteúdo do e-mail")

if st.button("Analisar e-mail"):
    score = score_texto(email)

    if score >= 4:
        st.error("🚨 E-mail suspeito")
    elif score >= 2:
        st.warning("⚠️ E-mail com sinais de risco")
    else:
        st.success("🟢 Baixo risco")

    st.write("**Score:**", score)
    registrar("email", score, email[:150])

# =========================
# HISTÓRICO
# =========================

st.header("📊 Histórico SOC")

if historico:
    df = pd.DataFrame(historico)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nenhum evento registrado ainda.")

# =========================
# PAINEL
# =========================

st.header("📡 Painel SOC")

eventos = len(historico)
suspeitos = len([e for e in historico if e.get("score", 0) >= 2])
alertas = len([e for e in historico if e.get("score", 0) >= 4])

c1, c2, c3 = st.columns(3)
c1.metric("Eventos detectados", eventos)
c2.metric("Eventos suspeitos", suspeitos)
c3.metric("Alertas ativos", alertas)

# =========================
# RADAR
# =========================

st.header("🛰️ Radar de ameaça")

if alertas >= 5:
    st.error("🚨 Nível alto de ameaça")
elif alertas >= 1:
    st.warning("⚠️ Atividade suspeita")
else:
    st.success("🟢 Ambiente seguro")

# =========================
# RELATÓRIO
# =========================

st.header("📄 Gerar relatório")

if st.button("Gerar relatório PDF"):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    y = 800
    c.drawString(50, y, "Relatório Escudo Digital IA")
    y -= 40

    for e in historico:
        linha = f"{e.get('data')} | {e.get('tipo')} | score:{e.get('score')}"
        c.drawString(50, y, linha)
        y -= 20

    c.save()

    st.download_button(
        "Baixar relatório",
        buffer.getvalue(),
        "relatorio_soc.pdf"
    )
