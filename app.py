import streamlit as st
import requests

st.set_page_config(page_title="Escudo Digital IA")

st.title("🛡️ ESCUDO DIGITAL IA")
st.write("Detector de golpes + análise de IP")

# ======================
# Detector de IP
# ======================

st.header("🌍 Detector de localização do IP")

ip = st.text_input("Digite domínio ou IP", key="ip_lookup_1")
if st.button("Localizar IP", key="btn_ip_1"):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}")
        data = r.json()
        st.write("Organização:", data["org"])
    except:
        st.error("Não foi possível localizar o IP")


    try:
        r = requests.get(f"http://ip-api.com/json/{ip}")
        data = r.json()

        st.write("Cidade:", data["city"])
        st.write("Organização:", data["org"])

    except:
        st.error("Não foi possível localizar o IP")

# ======================
# Detector de golpes
# ======================

st.header("🧠 Detector de golpe")

texto = st.text_area("Cole a mensagem suspeita", key="msg_1")
import streamlit as st
import requests

st.set_page_config(page_title="Escudo Digital IA")

st.title("🛡️ ESCUDO DIGITAL IA")
st.write("Detector de golpes + análise de IP")

# ======================
# Detector de IP
# ======================

st.header("🌍 Detector de localização do IP")

ip = st.text_input("Digite domínio ou IP", key="ip_lookup_2")
if st.button("Localizar IP", key="btn_ip_2"):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}")

# ======================
# Detector de localização do IP
# ======================

st.header("🌍 Detector de localização do IP")

ip = st.text_input("Digite domínio ou IP", key="ip_lookup")

if st.button("Localizar IP", key="btn_ip"):

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

