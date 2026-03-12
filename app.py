import streamlit as st
import requests

st.set_page_config(page_title="Escudo Digital IA")

st.title("🛡️ ESCUDO DIGITAL IA")
st.write("Detector de golpes + análise de IP")

# ======================
# Detector de IP
# ======================

import requests

st.set_page_config(page_title="Escudo Digital IA")

st.title("🛡️ ESCUDO DIGITAL IA")
st.write("Detector de golpes + análise de IP")

# ======================
# Detector de IP
# ======================


# ======================
# Mapa mundial de IP
# ======================

import folium
from streamlit_folium import st_folium

st.header("🌎 Mapa mundial de origem do IP")

ip_mapa = st.text_input("Digite IP para ver no mapa", key="mapa_ip")

if st.button("Mostrar no mapa", key="btn_mapa"):

    try:
        r = requests.get(f"http://ip-api.com/json/{ip_mapa}")
        data = r.json()

        lat = data["lat"]
        lon = data["lon"]

        mapa = folium.Map(location=[lat, lon], zoom_start=4)

        folium.Marker(
            [lat, lon],
            popup=f'{data["city"]} - {data["country"]}'
        ).add_to(mapa)

        st_folium(mapa, width=700)

    except:
        st.error("Não foi possível gerar o mapa")


# ======================
# Detector de localização do IP
# ======================

st.header("🌍 Detector de localização do IP")

ip = st.text_input("Digite domínio ou IP", key="ip_lookup")

if st.button("Localizar IP", key="btn_ip"):

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

