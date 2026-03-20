import streamlit as st
import hashlib
import json
import pandas as pd

# =========================
# CONFIG
# =========================
USERS_FILE = "usuarios.json"
ADMIN_EMAIL = "admin@escudo.com"

# =========================
# JSON
# =========================
def carregar_json(nome, padrao):
    try:
        with open(nome, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return padrao

def salvar_json(nome, dados):
    with open(nome, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2)

usuarios = carregar_json(USERS_FILE, {})

# =========================
# SESSÃO
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False

if "email_usuario" not in st.session_state:
    st.session_state.email_usuario = ""

# =========================
# SEGURANÇA
# =========================
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def is_admin():
    return (
        st.session_state.logado and
        st.session_state.email_usuario == ADMIN_EMAIL
    )

# =========================
# LOGIN CENTRAL
# =========================
if not st.session_state.logado:

    st.title("🛡️ Escudo Digital IA")
    st.caption("Proteção contra golpes digitais")

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        opcao = st.selectbox(
            "Escolha",
            ["Entrar", "Criar conta", "Recuperar senha"]
        )

        if opcao == "Entrar":
            email = st.text_input("Email")
            senha = st.text_input("Senha", type="password")

            if st.button("Entrar", use_container_width=True):
                if not email or not senha:
                    st.warning("Preencha tudo")
                elif email in usuarios:
                    if usuarios[email]["senha"] == hash_senha(senha):
                        st.session_state.logado = True
                        st.session_state.email_usuario = email
                        st.rerun()
                    else:
                        st.error("Senha incorreta")
                else:
                    st.error("Conta não encontrada")

        elif opcao == "Criar conta":
            email = st.text_input("Novo email")
            senha = st.text_input("Nova senha", type="password")

            if st.button("Criar conta", use_container_width=True):
                if email in usuarios:
                    st.warning("Conta já existe")
                else:
                    usuarios[email] = {
                        "senha": hash_senha(senha),
                        "uso": 0,
                        "premium": False,
                        "premium_expira": ""
                    }
                    salvar_json(USERS_FILE, usuarios)
                    st.success("Conta criada!")

        elif opcao == "Recuperar senha":
            email = st.text_input("Email")
            senha = st.text_input("Nova senha", type="password")

            if st.button("Resetar", use_container_width=True):
                if email in usuarios:
                    usuarios[email]["senha"] = hash_senha(senha)
                    salvar_json(USERS_FILE, usuarios)
                    st.success("Senha atualizada")
                else:
                    st.error("Email não encontrado")

    st.stop()

# =========================
# SIDEBAR
# =========================
st.sidebar.success(f"👤 {st.session_state.email_usuario}")

if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.session_state.email_usuario = ""
    st.rerun()

# =========================
# WHATSAPP PAGAMENTO
# =========================
st.sidebar.markdown(
    "[📲 Enviar comprovante](https://wa.me/5513996469617?text=Olá,%20acabei%20de%20pagar%20o%20Escudo%20Digital%20Premium.%20Segue%20o%20comprovante.)"
)

# =========================
# HOME (SISTEMA)
# =========================

st.title("🛡️ Escudo Digital IA")

# 🔎 SCANNER DOMÍNIO
st.header("🔍 Scanner de domínio")
url = st.text_input("Digite URL suspeita")
if st.button("Analisar domínio"):
    st.success("Domínio analisado (simulação)")

# 📷 PRINT
st.header("📷 Analisar print de golpe")
file = st.file_uploader("Envie print")
if file:
    st.success("Imagem analisada (simulação)")

# 📧 EMAIL
st.header("📧 Analisar email suspeito")
email_text = st.text_area("Cole o email")
if st.button("Analisar email"):
    st.success("Email analisado (simulação)")

# 🌍 IP
st.header("🌍 Análise OSINT de IP")
ip = st.text_input("Digite IP ou domínio")
if st.button("Analisar IP"):
    st.success("IP analisado (simulação)")

# 🚨 PHISHING
st.header("🚨 Detector de Phishing")
msg = st.text_area("Cole mensagem suspeita")
if st.button("Analisar mensagem"):
    st.success("Mensagem analisada (simulação)")

# 📱 WHATSAPP
st.header("📱 Detector de golpes de WhatsApp")
zap = st.text_area("Cole conversa")
if st.button("Analisar WhatsApp"):
    st.success("Conversa analisada (simulação)")

# 📚 BIBLIOTECA
st.header("📚 Biblioteca de golpes")
st.write("""
- golpe_pix — pedido urgente de dinheiro  
- emprestimo_falso — crédito fácil falso  
- phishing_banco — login falso  
- extorsao — ameaça  
- golpe_whatsapp — troca de número  
""")

# =========================
# ADMIN
# =========================
if is_admin():
    st.header("🔧 Admin")

    st.write(usuarios)
