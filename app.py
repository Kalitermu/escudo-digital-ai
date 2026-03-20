import streamlit as st
import hashlib
import json
import pandas as pd
from PIL import Image
import pytesseract

st.set_page_config(layout="wide")

# =========================
# CONFIG
# =========================
USERS_FILE = "usuarios.json"
ADMIN_EMAIL = "joseluizariel@gmail.com"
PIX = "13996469617"

# =========================
# ESTILO
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#dbeafe,#bfdbfe);
}
h1,h2,h3 {
    color:#1e3a8a;
}
.stButton>button {
    background: linear-gradient(90deg,#2563eb,#1d4ed8);
    color:white;
    border-radius:12px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# JSON
# =========================
def load():
    try:
        return json.load(open(USERS_FILE))
    except:
        return {}

def save(data):
    json.dump(data, open(USERS_FILE,"w"), indent=2)

usuarios = load()

# =========================
# SESSÃO
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False
if "email" not in st.session_state:
    st.session_state.email = ""

# =========================
# FUNÇÕES
# =========================
def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

def analisar(txt):
    txt = txt.lower()
    risco = 0
    tipos = []

    if "pix" in txt: risco+=30; tipos.append("Pix")
    if "urgente" in txt: risco+=20; tipos.append("Urgência")
    if "senha" in txt or "login" in txt: risco+=30; tipos.append("Phishing")
    if "inss" in txt: risco+=40; tipos.append("Golpe INSS")
    if "empréstimo" in txt: risco+=30; tipos.append("Empréstimo falso")

    return risco, tipos

def score(r):
    st.progress(min(r/100,1.0))
    if r>=70:
        st.error(f"🚨 ALTO RISCO ({r}%)")
    elif r>=40:
        st.warning(f"⚠️ RISCO MÉDIO ({r}%)")
    else:
        st.success(f"✅ BAIXO RISCO ({r}%)")

# =========================
# LOGIN
# =========================
if not st.session_state.logado:

    st.title("🛡️ Escudo Digital IA")

    op = st.selectbox("Acessar",["Entrar","Criar conta"])
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Continuar"):
        if op=="Entrar":
            if email in usuarios and usuarios[email]["senha"]==hash_senha(senha):
                st.session_state.logado=True
                st.session_state.email=email
                st.rerun()
            else:
                st.error("Erro login")

        else:
            usuarios[email]={"senha":hash_senha(senha),"uso":0,"premium":False}
            save(usuarios)
            st.success("Conta criada")

    st.stop()

# =========================
# USUÁRIO
# =========================
email = st.session_state.email

st.sidebar.success(f"👤 {email}")
st.sidebar.markdown("## 💎 Premium")
st.sidebar.code(PIX)

st.sidebar.markdown(
    f"[📲 Enviar comprovante](https://wa.me/55{PIX}?text=paguei%20premium)"
)

if st.sidebar.button("Sair"):
    st.session_state.logado=False
    st.rerun()

# =========================
# SISTEMA
# =========================
st.title("🛡️ Central de Análise")

# =========================
# DOMÍNIO
# =========================
st.header("🔍 Scanner de domínio")
url = st.text_input("Digite URL")

if st.button("Analisar domínio"):
    if url:
        st.success("Dominio analisado (simulação)")

# =========================
# PRINT
# =========================
st.header("📷 Analisar print de golpe")

img = st.file_uploader("Envie imagem", type=["png","jpg"])

if img:
    image = Image.open(img)
    st.image(image)

    if st.button("Analisar imagem"):
        texto = pytesseract.image_to_string(image)
        st.text_area("Texto detectado", texto)

        risco, tipos = analisar(texto)
        score(risco)

# =========================
# EMAIL
# =========================
st.header("📧 Analisar email")
email_txt = st.text_area("Cole email")

if st.button("Analisar email"):
    risco, tipos = analisar(email_txt)
    score(risco)

# =========================
# WHATS
# =========================
st.header("📱 Golpe WhatsApp")
zap = st.text_area("Cole conversa")

if st.button("Analisar WhatsApp"):
    risco, tipos = analisar(zap)
    score(risco)

# =========================
# IDOSO
# =========================
st.header("👴 Golpe contra idoso")
idoso = st.text_area("Mensagem")

if st.button("Analisar golpe idoso"):
    risco, tipos = analisar(idoso)
    score(risco)

# =========================
# BIBLIOTECA
# =========================
st.header("📚 Biblioteca de golpes")

st.markdown("""
- 💸 golpe_pix  
- 🏦 emprestimo_falso  
- 🔐 phishing  
- ⚠️ extorsao  
- 📱 whatsapp  
- 👴 golpe_idoso  
""")

# =========================
# SOC
# =========================
st.header("📊 Painel SOC")

st.metric("Eventos",0)
st.metric("Suspeitos",0)
st.metric("Alertas",0)

st.success("🟢 Ambiente seguro")

# =========================
# ADMIN
# =========================
if email == ADMIN_EMAIL:
    st.header("🔧 Admin")

    df = pd.DataFrame([
        {"Email":u,"Uso":d["uso"],"Premium":d["premium"]}
        for u,d in usuarios.items()
    ])
    st.dataframe(df)
