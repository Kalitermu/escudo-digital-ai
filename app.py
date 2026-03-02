import streamlit as st
import re
from PIL import Image
import pytesseract

st.set_page_config(page_title="ESCUDO DIGITAL IA", layout="centered")

# ===== ESTILO PROFISSIONAL =====
st.markdown("""
<style>
body {background-color:#0f1117;}
h1,h2,h3 {color:#00ffd5;}
.stButton>button {
    background: linear-gradient(90deg,#00ffd5,#0088ff);
    color:black;
    border:none;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ ESCUDO DIGITAL IA")
st.subheader("Detector de golpes + detector de IA")

texto = st.text_area("Cole a mensagem suspeita:")

uploaded_file = st.file_uploader("Ou envie um PRINT", type=["png","jpg","jpeg"])

# ===== OCR =====
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagem enviada")
    texto_img = pytesseract.image_to_string(image)
    st.info("Texto detectado na imagem:")
    st.write(texto_img)
    texto += " " + texto_img

# ===== ANALISE =====
def analisar(msg):

    score = 0

    golpes = [
        "pix", "urgente", "clique aqui",
        "senha", "cartao", "premio",
        "ganhou", "transferencia"
    ]

    ia_palavras = [
        "como modelo de linguagem",
        "sou uma ia",
        "gerado por ia",
        "assistente virtual"
    ]

    for g in golpes:
        if g in msg.lower():
            score += 15

    risco = "🟢 Seguro"
    if score > 20:
        risco = "🟠 Suspeito"
    if score > 40:
        risco = "🔴 Possível golpe"

    tipo = "👤 Parece humano"
    for i in ia_palavras:
        if i in msg.lower():
            tipo = "🤖 Parece IA"

    return risco, tipo, score

if st.button("ANALISAR 🔎"):

    if texto.strip() == "":
        st.warning("Digite algo ou envie um print.")
    else:
        risco, tipo, score = analisar(texto)

        st.success(f"Nível de risco: {risco}")
        st.info(f"Origem provável: {tipo}")
        st.metric("Score de risco", score)
