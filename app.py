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
    border-radius: 12px;
    height: 48px;
    font-weight: bold;
}
.stTextArea textarea {
    background-color: #f5faff;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🔐 HASH SENHA
# =========================
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# =========================
# 📂 ARQUIVOS
# =========================
ARQ_USUARIOS = "usuarios.json"
ARQ_LOGS = "logs.json"
ARQ_PAGAMENTOS = "pagamentos.json"

def carregar_json(arq):
    if os.path.exists(arq):
        with open(arq, "r") as f:
            return json.load(f)
    return []

def salvar_json(arq, dados):
    with open(arq, "w") as f:
        json.dump(dados, f, indent=4)

usuarios_db = carregar_json(ARQ_USUARIOS)
if not isinstance(usuarios_db, dict):
    usuarios_db = {}

# =========================
# 📊 LOGS
# =========================
def salvar_log(email):
    logs = carregar_json(ARQ_LOGS)
    logs.append({"email": email})
    salvar_json(ARQ_LOGS, logs)

def salvar_pagamento(email):
    pagamentos = carregar_json(ARQ_PAGAMENTOS)
    pagamentos.append({"email": email})
    salvar_json(ARQ_PAGAMENTOS, pagamentos)

def salvar_usuarios():
    salvar_json(ARQ_USUARIOS, usuarios_db)

# =========================
# IA
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

if "suspeitos" not in st.session_state:
    st.session_state.suspeitos = 0

# =========================
# IA + DETECÇÃO
# =========================
def analisar_texto(texto):
    try:
        texto_lower = texto.lower()

        if any(p in texto_lower for p in ["senha","pix","urgente","código","clique","link"]):
            resultado = """🔴 RISCO ALTO
⚠️ Possível golpe detectado automaticamente.
💡 Nunca envie dados ou dinheiro."""
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

        if any(p in texto_lower for p in ["pix","senha","urgente"]):
            st.session_state.suspeitos += 1

        return resultado

    except:
        return "⚠️ Sistema funcionando sem IA"

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

    st.title("🔐 Escudo Digital")

    opcao = st.radio("Acesso", ["Entrar", "Criar conta", "Recuperar senha"])

    if opcao == "Entrar":
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if email in usuarios_db and usuarios_db[email]["senha"] == hash_senha(senha):
                st.session_state.logado = True
                st.session_state.usuario = email
                salvar_log(email)
                st.success("Login realizado")
                st.rerun()
            else:
                st.error("Login inválido")

    elif opcao == "Criar conta":
        novo_email = st.text_input("Novo email")
        nova_senha = st.text_input("Nova senha", type="password")

        if st.button("Cadastrar"):
            usuarios_db[novo_email] = {
                "senha": hash_senha(nova_senha),
                "premium": False
            }
            salvar_usuarios()
            st.success("Conta criada")

    elif opcao == "Recuperar senha":
        email = st.text_input("Email")

        if st.button("Recuperar"):
            if email in usuarios_db:
                st.info("Senha protegida (criptografada)")
            else:
                st.error("Email não encontrado")

    st.stop()

# =========================
# APP
# =========================
st.title("🛡️ Escudo Digital IA")
st.caption("Proteção contra golpes digitais")

# PREMIUM
st.subheader("💎 Premium")
st.code("13996469617")

# ANALISE
st.subheader("🔍 Análise")
txt = st.text_area("Mensagem")

if st.button("Analisar"):
    resultado = analisar_texto(txt)

    if "ALTO" in resultado:
        st.error(resultado)
    else:
        st.success(resultado)

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
st.metric("Suspeitos", st.session_state.suspeitos)

# ADMIN
st.subheader("🔧 Admin")
user = st.session_state.usuario

st.write(user)
st.write("Premium:", usuarios_db[user]["premium"])

if st.button("Ativar Premium"):
    usuarios_db[user]["premium"] = True
    salvar_usuarios()
    salvar_pagamento(user)

if st.button("Sair"):
    st.session_state.logado = False
    st.rerun()

# =========================
# HISTÓRICO
# =========================
st.subheader("📊 Histórico de Acessos")
for l in carregar_json(ARQ_LOGS):
    st.write("👤", l["email"])

st.subheader("💰 Pagamentos")
for p in carregar_json(ARQ_PAGAMENTOS):
    st.write("💎", p["email"])

# =========================
# USUÁRIOS
# =========================
st.subheader("👥 Usuários")
for u in usuarios_db:
    status = "🟢 Premium" if usuarios_db[u]["premium"] else "⚪ Free"
    st.write(f"{u} — {status}")
