import streamlit as st
import json
import os
from openai import OpenAI
from PIL import Image
import pytesseract
import requests

# =========================
# 🎨 ESTILO AZUL CLARO PRO
# =========================
st.set_page_config(page_title="Escudo Digital IA", layout="centered")

st.markdown("""
<style>

/* FUNDO */
.stApp {
    background: linear-gradient(180deg, #dbeafe, #ffffff);
}

/* TITULOS */
h1, h2, h3 {
    color: #0b3c8c;
    font-weight: 700;
}

/* BOTÕES */
.stButton>button {
    background: linear-gradient(90deg, #1e88e5, #42a5f5);
    color: white;
    border-radius: 12px;
    height: 50px;
    font-weight: bold;
    border: none;
}

/* TEXTAREA */
.stTextArea textarea {
    background-color: #f0f7ff;
    border-radius: 10px;
}

/* CARD */
.block-container {
    padding-top: 2rem;
}

/* CAIXAS */
.stAlert {
    border-radius: 12px;
}

/* PREMIUM BOX */
code {
    background-color: #e3f2fd !important;
    color: #0d47a1 !important;
    font-size: 18px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# CONFIG IA
# =========================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# BANCO SIMPLES
# =========================
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {
        "joseluizariel@gmail.com": {"senha": "123", "premium": True}
    }

if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "eventos" not in st.session_state:
    st.session_state.eventos = 0

if "alertas" not in st.session_state:
    st.session_state.alertas = 0

if "suspeitos" not in st.session_state:
    st.session_state.suspeitos = 0

# =========================
# IA + DETECÇÃO LOCAL
# =========================
def analisar_texto(texto):
    try:
        if any(p in texto.lower() for p in ["senha", "pix", "urgente", "código", "clique aqui"]):
            resultado = "🔴 RISCO ALTO\n⚠️ Possível golpe detectado.\n💡 Nunca envie dados ou dinheiro."
        else:
            resposta = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Analise golpes digitais e classifique risco."},
                    {"role": "user", "content": texto}
                ]
            )
            resultado = resposta.choices[0].message.content

        st.session_state.eventos += 1

        if "ALTO" in resultado:
            st.session_state.alertas += 1

        if any(p in texto.lower() for p in ["pix", "senha", "urgente"]):
            st.session_state.suspeitos += 1

        return resultado

    except:
        return "⚠️ IA indisponível (sem saldo)"

# =========================
# OSINT IP
# =========================
def consultar_ip(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}").json()
        return f"""
🌍 País: {r.get('country')}
🏙️ Cidade: {r.get('city')}
📡 ISP: {r.get('isp')}
📍 Região: {r.get('regionName')}
📌 Lat: {r.get('lat')} | Lon: {r.get('lon')}
"""
    except:
        return "Erro ao consultar IP"

# =========================
# LOGIN
# =========================
if not st.session_state.logado:
    st.title("🔐 Login Escudo Digital")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if email in st.session_state.usuarios and st.session_state.usuarios[email]["senha"] == senha:
            st.session_state.logado = True
            st.session_state.usuario = email
            st.success("Login realizado")
        else:
            st.error("Login inválido")

    st.stop()

# =========================
# APP
# =========================
st.title("🛡️ Escudo Digital IA")
st.caption("Proteção contra golpes digitais")

st.markdown("## 🚨 Detecte golpes antes de perder dinheiro")

# PREMIUM
st.subheader("💎 Premium")
st.code("13996469617")
st.link_button("📲 Enviar comprovante", "https://wa.me/5513996469617")

# =========================
# ANÁLISE
# =========================
st.subheader("🔍 Central de Análise")
texto = st.text_area("Cole mensagem suspeita")

if st.button("🚀 Analisar agora"):
    if texto:
        resultado = analisar_texto(texto)

        if "ALTO" in resultado:
            st.error(resultado)
        elif "MÉDIO" in resultado:
            st.warning(resultado)
        else:
            st.success(resultado)

        st.progress(min(st.session_state.eventos / 10, 1.0))

# =========================
# PRINT
# =========================
st.subheader("📷 Analisar print")
img = st.file_uploader("Envie imagem")

if img:
    imagem = Image.open(img)
    texto_img = pytesseract.image_to_string(imagem)
    st.text_area("Texto detectado", texto_img)

    if st.button("🔎 Analisar imagem"):
        st.success(analisar_texto(texto_img))

# =========================
# OSINT
# =========================
st.subheader("🌍 OSINT - Análise de IP")
ip = st.text_input("Digite IP")

if st.button("🌐 Consultar OSINT"):
    if ip:
        st.info(consultar_ip(ip))

# =========================
# OUTROS
# =========================
st.subheader("📧 Email")
st.text_area("Cole email")

st.subheader("📱 WhatsApp")
st.text_area("Cole conversa")

st.subheader("👴 Golpe INSS")
st.text_area("Mensagem")

# =========================
# BIBLIOTECA
# =========================
st.subheader("📚 Biblioteca")
st.write("- 💸 golpe_pix")
st.write("- 🔐 phishing")
st.write("- 📱 whatsapp")

# =========================
# SOC
# =========================
st.subheader("📊 Painel SOC")

st.metric("Eventos", st.session_state.eventos)
st.metric("Suspeitos", st.session_state.suspeitos)
st.metric("Alertas", st.session_state.alertas)

if st.session_state.alertas > 0:
    st.error("⚠️ Ameaças detectadas")
else:
    st.success("🟢 Ambiente seguro")

# =========================
# ADMIN
# =========================
st.subheader("🔧 Admin")

usuario = st.session_state.usuario
premium = st.session_state.usuarios[usuario]["premium"]

st.write(f"Usuário: {usuario}")
st.write(f"Premium: {'✅ Ativo' if premium else '❌ Não'}")

if st.button("Ativar Premium"):
    st.session_state.usuarios[usuario]["premium"] = True
    st.success("Premium ativado")

if st.button("Remover Premium"):
    st.session_state.usuarios[usuario]["premium"] = False

if st.button("Sair"):
    st.session_state.logado = False
    st.rerun()

# =========================
# USUÁRIOS
# =========================
st.subheader("👥 Usuários")

for u in st.session_state.usuarios:
    status = "🟢 Premium" if st.session_state.usuarios[u]["premium"] else "❌"
    st.write(f"{u} — {status}")
