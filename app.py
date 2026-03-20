import streamlit as st
import hashlib
import json
import pandas as pd

st.set_page_config(page_title="Escudo Digital IA", layout="wide")

# =========================
# CONFIG
# =========================
USERS_FILE = "usuarios.json"
ADMIN_EMAIL = "joseluizariel@gmail.com"
PIX_CHAVE = "13996469617"

# =========================
# ESTILO
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
}
h1, h2, h3 {
    color: #1e3a8a;
}
.stButton>button {
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    color: white;
    border-radius: 12px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =========================
# JSON
# =========================
def carregar_json(nome, padrao):
    try:
        with open(nome, "r") as f:
            return json.load(f)
    except:
        return padrao

def salvar_json(nome, dados):
    with open(nome, "w") as f:
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
# FUNÇÕES
# =========================
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def is_admin():
    return st.session_state.email_usuario == ADMIN_EMAIL

def verificar_limite():
    if not usuarios[email]["premium"] and usuarios[email]["uso"] >= 7:
        st.error("🚫 Limite grátis atingido")
        st.stop()

def usar():
    usuarios[email]["uso"] += 1
    salvar_json(USERS_FILE, usuarios)

def analisar_texto(texto):
    texto = texto.lower()
    risco = 0
    tipo = []

    if "pix" in texto:
        risco += 30; tipo.append("Pix")
    if "urgente" in texto or "agora" in texto:
        risco += 20; tipo.append("Urgência")
    if "senha" in texto or "login" in texto or "clique" in texto:
        risco += 30; tipo.append("Phishing")
    if "inss" in texto or "aposentadoria" in texto:
        risco += 40; tipo.append("INSS")
    if "empréstimo" in texto or "taxa" in texto:
        risco += 30; tipo.append("Financeiro suspeito")

    return risco, tipo

def mostrar_score(risco):
    st.progress(min(risco/100,1.0))
    if risco >= 70:
        st.error(f"🚨 ALTO RISCO ({risco}%)")
    elif risco >= 40:
        st.warning(f"⚠️ RISCO MÉDIO ({risco}%)")
    else:
        st.success(f"✅ BAIXO RISCO ({risco}%)")

# =========================
# LOGIN
# =========================
if not st.session_state.logado:

    st.title("🛡️ Escudo Digital IA")
    st.caption("Proteção inteligente contra golpes")

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        opcao = st.selectbox("Acessar", ["Entrar", "Criar conta"])
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Continuar", use_container_width=True):

            if opcao == "Entrar":
                if email in usuarios and usuarios[email]["senha"] == hash_senha(senha):
                    st.session_state.logado = True
                    st.session_state.email_usuario = email
                    st.rerun()
                else:
                    st.error("Login inválido")

            else:
                usuarios[email] = {
                    "senha": hash_senha(senha),
                    "uso": 0,
                    "premium": False
                }
                salvar_json(USERS_FILE, usuarios)
                st.success("Conta criada")

    st.stop()

# =========================
# USUÁRIO
# =========================
email = st.session_state.email_usuario

st.sidebar.success(f"👤 {email}")
st.sidebar.info(f"📊 Usos: {usuarios[email]['uso']} / 7 grátis")

st.sidebar.markdown("## 💎 Premium")
st.sidebar.code(PIX_CHAVE)

st.sidebar.markdown(
    f"[📲 Enviar comprovante](https://wa.me/55{PIX_CHAVE}?text=Olá,%20paguei%20o%20Escudo%20Digital%20Premium)"
)

if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()

# =========================
# SISTEMA
# =========================
st.title("🛡️ Central de Análise")

entrada = st.text_area("Cole qualquer mensagem suspeita")

if st.button("🔍 Analisar agora", use_container_width=True):

    if entrada:
        verificar_limite()
        usar()

        risco, tipo = analisar_texto(entrada)

        mostrar_score(risco)

        st.markdown("### 🔎 Tipos detectados")
        for t in tipo:
            st.markdown(f"- ⚠️ {t}")
    else:
        st.warning("Digite algo")

# =========================
# BIBLIOTECA
# =========================
st.header("📚 Tipos de golpes")

st.markdown("""
- 💸 Pix falso  
- 🏦 Empréstimo falso  
- 🔐 Phishing  
- ⚠️ Extorsão  
- 📱 WhatsApp clonado  
- 👴 Golpe INSS  
""")

# =========================
# ADMIN
# =========================
if is_admin():
    st.header("🔧 Painel Admin")

    df = pd.DataFrame([
        {"Email": u, "Uso": d["uso"], "Premium": d["premium"]}
        for u, d in usuarios.items()
    ])

    st.dataframe(df)

    user_sel = st.selectbox("Selecionar usuário", list(usuarios.keys()))

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Ativar Premium"):
            usuarios[user_sel]["premium"] = True
            salvar_json(USERS_FILE, usuarios)
            st.success("Ativado")

    with col2:
        if st.button("Remover Premium"):
            usuarios[user_sel]["premium"] = False
            salvar_json(USERS_FILE, usuarios)
            st.warning("Removido")
