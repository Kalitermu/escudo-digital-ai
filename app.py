
import streamlit as st

# ======================
# Relatório SOC
# ======================

st.header("📄 Relatório de análise")

if st.button("Gerar relatório SOC"):

    st.write("### Resultado da análise")

    ip = "N/A"

    st.write("IP analisado:", ip)

    if "data" in locals():
        if data["status"] == "success":
            st.write("País:", data["country"])
            st.write("Cidade:", data["city"])
            st.write("Organização:", data["org"])
