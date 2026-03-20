import streamlit as st
import hashlib
import json
import pandas as pd

# =========================
# 🎨 ESTILO (FUNDO AZUL)
# =========================
st.set_page_config(page_title="Escudo Digital IA", layout="centered")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e3a8a);
    color: white;
}
h1, h2, h3, h4 {
    color: white;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background-color: #1e293b;
    color: white;
    border-radius: 10px;
}
.stButton>button {
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    color: white;
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =========================
# CONFIG
# =========================
USERS_FILE = "usuarios.json"
ADMIN_EMAIL = "joseluizariel@gmail.com"

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

def is_premium():
    return usuarios.get(st.session_state.email_usuario, {}).get("premium", False)

# =========================
# LOGIN CENTRAL
# =========================
if not st.session_state.logado:

    st.title("🛡️ Escudo Digital IA")
    st.caption("Proteção contra golpes digitais")

    opcao = st.selectbox("Escolha", ["Entrar", "Criar conta", "Recuperar senha"])

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if opcao == "Entrar":
        if st.button("Entrar", use_container_width=True):
            if email in usuarios and usuarios[email]["senha"] == hash_senha(senha):
                st.session_state.logado = True
                st.session_state.email_usuario = email
                st.rerun()
            else:
                st.error("Login inválido")

    elif opcao == "Criar conta":
        if st.button("Criar conta", use_container_width=True):
            if email in usuarios:
                st.warning("Já existe")
            else:
                usuarios[email] = {
                    "senha": hash_senha(senha),
                    "uso": 0,
                    "premium": False,
                    "premium_expira": ""
                }
                salvar_json(USERS_FILE, usuarios)
                st.success("Conta criada")

    elif opcao == "Recuperar senha":
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

st.sidebar.markdown(
    "[📲 Enviar comprovante](https://wa.me/5513996469617?text=Olá,%20acabei%20de%20pagar%20o%20Escudo%20Digital%20Premium.)"
)

if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()

# =========================
# HOME
# =========================
st.title("🛡️ Escudo Digital IA")

# 🔍 DOMÍNIO
st.header("🔍 Scanner de domínio")
url = st.text_input("Digite URL suspeita")
if st.button("Analisar domínio"):
    if not is_premium():
        st.error("🔒 Premium necessário")
    else:
        st.success("Analisado")

# 📧 EMAIL
st.header("📧 Email suspeito")
email_text = st.text_area("Cole o email")
if st.button("Analisar email"):
    if not is_premium():
        st.error("🔒 Premium necessário")
    else:
        st.success("Analisado")

# 📱 WHATSAPP
st.header("📱 Golpe WhatsApp")
zap = st.text_area("Cole conversa")
if st.button("Analisar WhatsApp"):
    if not is_premium():
        st.error("🔒 Premium necessário")
    else:
        st.success("Analisado")

# 📚 BIBLIOTECA
st.header("📚 Biblioteca de golpes")
st.write("""
• golpe_pix  
• emprestimo_falso  
• phishing  
• extorsao  
• whatsapp  
""")

# =========================
# ADMIN
# =========================
if is_admin():
    st.header("🔧 Admin")

    st.dataframe(pd.DataFrame([
        {
            "Email": email,
            "Uso": dados.get("uso", 0),
            "Premium": dados.get("premium", False)
        }
        for email, dados in usuarios.items()
    ]))
