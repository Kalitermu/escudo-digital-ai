import streamlit as st
import requests

st.set_page_config(page_title="Escudo Digital IA")

st.title("🛡️ ESCUDO DIGITAL IA")
st.write("Detector de golpes + análise de IP")

# ======================
# Detector de IP
# ======================

st.header("🌍 Detector de localização do IP")

ip = st.text_input("Digite domínio ou IP")

if st.button("Localizar IP"):

    try:
        r = requests.get(f"http://ip-api.com/json/{ip}")
        data = r.json()

        st.success("IP encontrado")

        st.write("IP:", data["query"])
        st.write("País:", data["country"])
        st.write("Cidade:", data["city"])
        st.write("Organização:", data["org"])

    except:
        st.error("Não foi possível localizar o IP")

# ======================
# Detector de golpes
# ======================

st.header("🧠 Detector de golpe")

texto = st.text_area("Cole a mensagem suspeita")
import streamlit as st
import requests

st.set_page_config(page_title="Escudo Digital IA")

st.title("🛡️ ESCUDO DIGITAL IA")
st.write("Detector de golpes + análise de IP")

# ======================
# Detector de IP
# ======================

st.header("🌍 Detector de localização do IP")

ip = st.text_input("Digite domínio ou IP")

if st.button("Localizar IP"):

    try:
        r = requests.get(f"http://ip-api.com/json/{ip}")
        data = r.json()

        st.success("IP encontrado")

        st.write("IP:", data["query"])
        st.write("País:", data["country"])
        st.write("Cidade:", data["city"])
        st.write("Organização:", data["org"])

    except:
        st.error("Não foi possível localizar o IP")

if st.button("Localizar IP"):

    try:
        r = requests.get(f"http://ip-api.com/json/{ip}")
        data = r.json()

        st.success("IP encontrado")

        st.write("IP:", data["query"])
        st.write("País:", data["country"])
        st.write("Cidade:", data["city"])
        st.write("Organização:", data["org"])

    except:
        st.error("Não foi possível localizar o IP")

# ======================
# Detector de golpes
# ======================

st.header("🧠 Detector de golpe")

texto = st.text_area("Cole a mensagem suspeita")

if st.button("Analisar mensagem"):

    palavras = [
        "pix","senha","codigo","urgente",
        "transferencia","banco","login",
        "verificacao","confirmar"
    ]

    score = 0

    for p in palavras:
        if p in texto.lower():
            score += 15

    st.write("Score de risco:", score)

    if score >= 40:
        st.error("🚨 Alto risco de golpe")

    elif score >= 20:
        st.warning("⚠️ Mensagem suspeita")

    else:
        st.success("Baixo risco")

# ======================
# Radar SOC
# ======================

import random

st.header("📡 RADAR SOC")

col1, col2, col3 = st.columns(3)

col1.metric("Threat Level", random.randint(10,90))
col2.metric("Shield", random.randint(60,100))
col3.metric("Scan Integrity", random.randint(80,100))

# =========================
# Localização de IP
# =========================

import socket
import requests

st.header("🌍 Detector de localização do IP")

ip = st.text_input("Digite domínio ou IP", key="ip_lookup")
if st.button("Localizar IP"):

if st.button("Localizar IP"):

    try:
        ip_resolvido = socket.gethostbyname(ip)

        r = requests.get(f"http://ip-api.com/json/{ip_resolvido}")
        data = r.json()

        st.success("IP encontrado")

        st.write("IP:", data["query"])
        st.write("País:", data["country"])
        st.write("Cidade:", data["city"])
        st.write("Região:", data["regionName"])
        st.write("Organização:", data["org"])

    except:
        st.error("Não foi possível localizar o IP")


import folium
from streamlit_folium import st_folium

st.header("🌍 Mapa de origem do IP")

ip = st.text_input("Digite um IP ou domínio")

if st.button("Localizar IP no mapa"):

    import requests
    r = requests.get(f"http://ip-api.com/json/{ip}")
    data = r.json()

    lat = data["lat"]
    lon = data["lon"]

    mapa = folium.Map(location=[lat, lon], zoom_start=4)

    folium.Marker(
        [lat, lon],
        popup=f"{data['city']} - {data['country']}"
    ).add_to(mapa)

    st_folium(mapa, width=700)

