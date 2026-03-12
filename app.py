import streamlit as st

st.markdown("""

<style>

body {

background: linear-gradient(135deg,#020617,#0f172a);

}

h1,h2,h3 {

color:#00ffa6;

text-shadow:0 0 10px #00ffa6;

}

.stButton>button {

background: linear-gradient(90deg,#00ffa6,#00bfff);

border-radius:12px;

color:black;

font-weight:bold;

}

</style>

""", unsafe_allow_html=True)

import streamlit as st
import requests
import random

st.set_page_config(page_title="Escudo Digital IA")

st.title("🛡️ ESCUDO DIGITAL IA")
st.write("Detector de golpes + análise de IP")

# ======================
# Detector de IP
# ======================

st.header("🌍 Detector de localização do IP")

ip = st.text_input("Digite domínio ou IP")

if st.button("Localizar IP"):

    r = requests.get(f"http://ip-api.com/json/{ip}")
    data = r.json()

    if data["status"] == "success":

        st.success("IP encontrado")

        st.write("IP:", data["query"])
        st.write("País:", data["country"])
        st.write("Cidade:", data["city"])
        st.write("Organização:", data["org"])

    else:
        st.error("Não foi possível localizar o IP")


# ======================
# Radar SOC
# ======================

st.header("📡 RADAR SOC REAL")

col1,col2,col3 = st.columns(3)

col1.metric("Threat Level", random.randint(10,90))
col2.metric("Shield Power", random.randint(60,100))
col3.metric("Scan Integrity", random.randint(80,100))


# ======================
# Detector de golpe
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
