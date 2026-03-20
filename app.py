import streamlit as st
import json
import os
import hashlib
from openai import OpenAI
from PIL import Image
import pytesseract
import requests

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Escudo Digital IA", layout="centered")

# =========================
# 🎨 ESTILO
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #e6f0ff, #ffffff);
}
h1, h2, h3 {
    color: #0d47a1;
}
.stButton>button {
    background-color: #1e88e5;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🔐 HASH SENHA
# =========================
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# =========================
# 💾 BANCO JSON
# =========================
ARQ_USUARIOS = "usuarios.json"

def carregar_usuarios():
    if os.path.exists(ARQ_USUARIOS):
        with open(ARQ_USUARIOS, "r") as f:
            return json.load(f)
    return {}

def salvar_usuarios(dados):
    with open(ARQ_USUARIOS, "w") as f:
        json.dump(dados, f, indent=4)

usuarios_db = carregar_usuarios()

# =========================
# CONFIG IA
# =========================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# SESSION
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "eventos" not in st.session_state:
    st.session_state.eventos = 0

if "alertas" not in st.session_state:
    st.session_state.alertas = 0

# =========================
# IA + LOCAL
# =========================
def analisar_texto(texto):
    try:
        if any(p in texto.lower() for p in ["senha","pix","urgente","código","clique"]):
            resultado = "🔴 RISCO ALTO\n⚠️ Possível golpe detectado.\n💡 Nunca envie dados ou dinheiro."
        else:
            resposta = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Analise golpes digitais"},
                    {"role": "user", "content": texto}
                ]
            )
            resultado = resposta.choices[0].message.content

        st.session_state.eventos += 1

        if "ALTO" in resultado:
            st.session_state.alertas += 1

        return resultado

    except:
        return "⚠️ IA indisponível (sem saldo)"

# =========================
# OSINT
# =========================
def consultar_ip(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}").json()
        return f"{r.get('country')} | {r.get('city')} | {r.get('isp')}"
    except:
        return "Erro OSINT"

# =========================
# LOGIN / CADASTRO
# =========================
if not st.session_state.logado:

    st.title("🔐 Login Escudo Digital")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if email in usuarios_db and usuarios_db[email]["senha"] == hash_senha(senha):
            st.session_state.logado = True
            st.session_state.usuario = email
            st.success("Login OK")
        else:
            st.error("Login inválido")

    # CADASTRO
    st.subheader("Criar conta")
    new_email = st.text_input("Novo email")
    new_pass = st.text_input("Nova senha", type="password")

    if st.button("Cadastrar"):
        if new_email and new_pass:
            usuarios_db[new_email] = {
                "senha": hash_senha(new_pass),
                "premium": False
            }
            salvar_usuarios(usuarios_db)
            st.success("Conta criada")

    # RECUPERAR
    st.subheader("Recuperar senha")
    rec_email = st.text_input("Email recuperar")

    if st.button("Recuperar"):
        if rec_email in usuarios_db:
            st.info("Senha protegida (criptografada)")
        else:
            st.error("Email não encontrado")

    st.stop()

# =========================
# APP
# =========================
st.title("🛡️ Escudo Digital IA")

# PREMIUM
st.subheader("💎 Premium")
st.code("13996469617")

# ANALISE
st.subheader("🔍 Análise")
txt = st.text_area("Mensagem")

if st.button("Analisar"):
    st.success(analisar_texto(txt))

# PRINT
st.subheader("📷 Print")
img = st.file_uploader("Imagem")

if img:
    texto_img = pytesseract.image_to_string(Image.open(img))
    st.text(texto_img)

# OSINT
st.subheader("🌍 OSINT")
ip = st.text_input("IP")

if st.button("Consultar"):
    st.info(consultar_ip(ip))

# SOC
st.subheader("📊 SOC")
st.metric("Eventos", st.session_state.eventos)
st.metric("Alertas", st.session_state.alertas)

# ADMIN
st.subheader("Admin")
user = st.session_state.usuario

if user in usuarios_db:
    st.write(user)
    st.write("Premium:", usuarios_db[user]["premium"])

if st.button("Ativar Premium"):
    usuarios_db[user]["premium"] = True
    salvar_usuarios(usuarios_db)

if st.button("Sair"):
    st.session_state.logado = False
    st.rerun()
