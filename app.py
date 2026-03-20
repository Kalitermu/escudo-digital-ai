import streamlit as st
import json
import os
from openai import OpenAI
from PIL import Image
import pytesseract
import requests

# =========================
# 🎨 ESTILO
# =========================
st.set_page_config(page_title="Escudo Digital IA", layout="centered")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #dbeafe, #ffffff);
}

h1, h2, h3 {
    color: #0b3c8c;
    font-weight: 700;
}

.stButton>button {
    background: linear-gradient(90deg, #1e88e5, #42a5f5);
    color: white;
    border-radius: 12px;
    height: 50px;
    font-weight: bold;
}

.stTextArea textarea {
    background-color: #f0f7ff;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# IA
# =========================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# BANCO
# =========================
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {
        "joseluizariel@gmail.com": {"senha": "123", "premium": True}
    }

if "tela" not in st.session_state:
    st.session_state.tela = "login"

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
# FUNÇÕES
# =========================
def analisar_texto(texto):
    try:
        if any(p in texto.lower() for p in ["senha", "pix", "urgente", "código"]):
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

        if any(p in texto.lower() for p in ["pix", "senha"]):
            st.session_state.suspeitos += 1

        return resultado

    except:
        return "⚠️ IA indisponível"

def consultar_ip(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}").json()
        return f"{r.get('country')} - {r.get('city')} - {r.get('isp')}"
    except:
        return "Erro OSINT"

# =========================
# TELAS
# =========================

# LOGIN
if st.session_state.tela == "login":
    st.title("🔐 Login Escudo Digital")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if email in st.session_state.usuarios and st.session_state.usuarios[email]["senha"] == senha:
            st.session_state.logado = True
            st.session_state.usuario = email
            st.session_state.tela = "app"
            st.rerun()
        else:
            st.error("Login inválido")

    col1, col2 = st.columns(2)

    if col1.button("Criar conta"):
        st.session_state.tela = "cadastro"
        st.rerun()

    if col2.button("Recuperar senha"):
        st.session_state.tela = "recuperar"
        st.rerun()

    st.stop()

# CADASTRO
if st.session_state.tela == "cadastro":
    st.title("🆕 Criar conta")

    novo_email = st.text_input("Novo email")
    nova_senha = st.text_input("Nova senha", type="password")

    if st.button("Cadastrar"):
        if novo_email in st.session_state.usuarios:
            st.warning("Já existe")
        else:
            st.session_state.usuarios[novo_email] = {"senha": nova_senha, "premium": False}
            st.success("Conta criada")

    if st.button("Voltar"):
        st.session_state.tela = "login"
        st.rerun()

    st.stop()

# RECUPERAR
if st.session_state.tela == "recuperar":
    st.title("🔑 Recuperar senha")

    email = st.text_input("Email")

    if st.button("Recuperar"):
        if email in st.session_state.usuarios:
            st.success(f"Sua senha é: {st.session_state.usuarios[email]['senha']}")
        else:
            st.error("Email não encontrado")

    if st.button("Voltar"):
        st.session_state.tela = "login"
        st.rerun()

    st.stop()

# =========================
# APP (NÃO REMOVI NADA)
# =========================

st.title("🛡️ Escudo Digital IA")
st.caption("Proteção contra golpes digitais")

# PREMIUM
st.subheader("💎 Premium")
st.code("13996469617")

# ANALISE
st.subheader("🔍 Central de Análise")
texto = st.text_area("Mensagem")

if st.button("Analisar"):
    if texto:
        r = analisar_texto(texto)
        if "ALTO" in r:
            st.error(r)
        else:
            st.success(r)

# PRINT
st.subheader("📷 Analisar print")
img = st.file_uploader("Imagem")

if img:
    imagem = Image.open(img)
    texto_img = pytesseract.image_to_string(imagem)

    if st.button("Analisar imagem"):
        st.success(analisar_texto(texto_img))

# OSINT
st.subheader("🌍 OSINT")
ip = st.text_input("IP")

if st.button("Consultar"):
    st.info(consultar_ip(ip))

# SOC
st.subheader("📊 SOC")
st.metric("Eventos", st.session_state.eventos)
st.metric("Alertas", st.session_state.alertas)
st.metric("Suspeitos", st.session_state.suspeitos)

# ADMIN
st.subheader("🔧 Admin")

usuario = st.session_state.usuario
premium = st.session_state.usuarios[usuario]["premium"]

st.write(usuario)
st.write("Premium:", premium)

if st.button("Ativar Premium"):
    st.session_state.usuarios[usuario]["premium"] = True

if st.button("Sair"):
    st.session_state.tela = "login"
    st.session_state.logado = False
    st.rerun()

# USERS
st.subheader("👥 Usuários")
for u in st.session_state.usuarios:
    st.write(u)
