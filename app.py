import streamlit as st

st.title("🛡️ ESCUDO DIGITAL IA")
st.subheader("Detector de golpes e IA")
texto = st.text_area("Cole a mensagem suspeita:")

if st.button("Analisar"):
    st.success("Análise funcionando 🚀")
