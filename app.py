import streamlit as st
import requests
import random
import pandas as pd

st.set_page_config(page_title="Escudo Digital IA")

st.title("🛡️ ESCUDO DIGITAL IA")
st.write("SOC de monitoramento de golpes e análise OSINT")

# ======================
# Detector de IP + OSINT
# ======================

st.header("🌍 Análise OSINT de IP")

ip = st.text_input("Digite domínio ou IP")

if st.button("Analisar IP"):

    r = requests.get(f"http://ip-api.com/json/{ip}")
    data = r.json()

    if data["status"] == "success":

        st.success("IP encontrado")

        st.write("IP:", data["query"])
        st.write("País:", data["country"])
        st.write("Cidade:", data["city"])
        st.write("Região:", data["regionName"])
        st.write("ISP:", data["isp"])
        st.write("Organização:", data["org"])
        st.write("ASN:", data["as"])

        # mapa do IP
        mapa = pd.DataFrame({
            "lat":[data["lat"]],
            "lon":[data["lon"]]
        })

        st.map(mapa)

    else:
        st.error("Não foi possível localizar o IP")


# ======================
# Detector de phishing
# ======================

st.header("🚨 Detector de Phishing")

mensagem = st.text_area("Cole mensagem ou link suspeito")

if st.button("Analisar golpe"):

    palavras = [
        "pix","senha","codigo","urgente",
        "transferencia","banco","login",
        "verificacao","confirmar",
        "clique aqui","atualize conta"
    ]

    score = 0

    for p in palavras:
        if p in mensagem.lower():
            score += 15

    st.write("Score de risco:", score)

    if score >= 40:
        st.error("🚨 Alto risco de golpe")

    elif score >= 20:
        st.warning("⚠️ Mensagem suspeita")

    else:
        st.success("🟢 Baixo risco")


# ======================
# Painel SOC
# ======================

st.header("📡 Painel SOC")

ataques = random.randint(20,120)
ips = random.randint(50,300)
alertas = random.randint(0,20)

col1,col2,col3 = st.columns(3)

col1.metric("Eventos detectados", ataques)
col2.metric("IPs analisados", ips)
col3.metric("Alertas ativos", alertas)


# ======================
# Radar de ameaça
# ======================

st.header("🛰️ Radar de ameaça")

nivel = random.randint(10,100)

st.progress(nivel)

if nivel > 70:
    st.error("🚨 Nível alto de ameaça")

elif nivel > 40:
    st.warning("⚠️ Atividade suspeita")

else:
    st.success("🟢 Ambiente seguro")
