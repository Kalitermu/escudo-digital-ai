import streamlit as st
import hashlib
import json
import pandas as pd

# =========================
# CONFIG
# =========================
USERS_FILE = "usuarios.json"
ADMIN_EMAIL = "joseluizariel@gmail.com"
PIX_CHAVE = "13996469617"

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
# ESTILO (AZUL)
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}
button {
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOGIN CENTRAL
# =========================
if not st.session_state.logado:
    st.title("🛡️ Escudo Digital IA")
    st.subheader("Proteção contra golpes digitais")

    opcao = st.selectbox("Escolha", ["Entrar", "Criar conta"])

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Continuar"):

        if opcao == "Entrar":
            if email in usuarios and usuarios[email]["senha"] == hash_senha(senha):
                st.session_state.logado = True
                st.session_state.email_usuario = email
                st.success("Login feito")
                st.rerun()
            else:
                st.error("Login inválido")

        else:
            if email not in usuarios:
                usuarios[email] = {
                    "senha": hash_senha(senha),
                    "uso": 0,
                    "premium": False,
                    "premium_expira": ""
                }
                salvar_json(USERS_FILE, usuarios)

                st.session_state.logado = True
                st.session_state.email_usuario = email
                st.success("Conta criada")
                st.rerun()
            else:
                st.warning("Conta já existe")

    st.stop()

# =========================
# USUÁRIO LOGADO
# =========================
email = st.session_state.email_usuario

st.sidebar.success(f"👤 {email}")

if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()

# =========================
# PAGAMENTO PIX
# =========================
st.sidebar.markdown("## 💎 Premium")

st.sidebar.write("🔐 Libere tudo por apenas R$ 9,90")

st.sidebar.code(PIX_CHAVE)

st.sidebar.markdown(
    f"[📲 Enviar comprovante](https://wa.me/55{PIX_CHAVE}?text=Olá,%20acabei%20de%20pagar%20o%20Escudo%20Digital%20Premium.)"
)

# =========================
# LIMITE GRÁTIS
# =========================
def verificar_limite():
    if not usuarios[email]["premium"]:
        if usuarios[email]["uso"] >= 7:
            st.error("🚫 Limite grátis atingido")
            st.stop()

def usar():
    usuarios[email]["uso"] += 1
    salvar_json(USERS_FILE, usuarios)

# =========================
# SISTEMA
# =========================
st.title("🛡️ Escudo Digital IA")

# 🔍 DOMÍNIO
st.header("🔍 Scanner de domínio")
url = st.text_input("Digite URL")

if st.button("Analisar domínio"):
    verificar_limite()
    usar()
    st.success("Domínio analisado (simulação)")

# 📧 EMAIL
st.header("📧 Email suspeito")
email_texto = st.text_area("Cole o email")

if st.button("Analisar email"):
    verificar_limite()
    usar()
    st.success("Email analisado (simulação)")

# 📱 WHATSAPP
st.header("📱 Golpe WhatsApp")
zap = st.text_area("Cole conversa")

if st.button("Analisar WhatsApp"):
    verificar_limite()
    usar()
    st.success("Conversa analisada (simulação)")

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

    lista = []
    for u, d in usuarios.items():
        lista.append({
            "Email": u,
            "Uso": d["uso"],
            "Premium": d["premium"]
        })

    st.dataframe(pd.DataFrame(lista))

    user_sel = st.selectbox("Usuário", list(usuarios.keys()))

    if st.button("Ativar Premium"):
        usuarios[user_sel]["premium"] = True
        salvar_json(USERS_FILE, usuarios)
        st.success("Premium ativado")

    if st.button("Remover Premium"):
        usuarios[user_sel]["premium"] = False
        salvar_json(USERS_FILE, usuarios)
        st.warning("Premium removido")
