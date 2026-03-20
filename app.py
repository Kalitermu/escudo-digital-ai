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
# 🎨 ESTILO MELHORADO
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
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🔐 HASH
# =========================
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# =========================
# 💾 BANCO
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
# 🧠 IA + DETECÇÃO
# =========================
def analisar_texto(texto):
    try:
        texto_lower = texto.lower()

        # 🔥 DETECÇÃO LOCAL (NÃO DEPENDE DE IA)
        if any(p in texto_lower for p in ["senha","pix","urgente","código","clique","link"]):
            resultado = """🔴 RISCO ALTO
⚠️ Possível golpe detectado automaticamente.
💡 Nunca envie dados ou dinheiro."""
        else:
            resposta = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Analise golpes digitais e classifique risco."},
                    {"role": "user", "content": texto}
                ]
            )
            resultado = resposta.choices[0].message.content

        # SOC
        st.session_state.eventos += 1

        if "ALTO" in resultado:
            st.session_state.alertas += 1

        if any(p in texto_lower for p in ["pix","senha","urgente"]):
            st.session_state.suspeitos += 1

        return resultado

    except:
        return "⚠️ Sistema funcionando em modo básico (sem IA ativa)"

# =========================
# 🌍 OSINT
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
# LOGIN / CADASTRO
# =========================
if not st.session_state.logado:

    st.title("🔐 Escudo Digital")

    opcao = st.radio("Acesso", ["Entrar", "Criar conta", "Recuperar senha"])

    # LOGIN
    if opcao == "Entrar":
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if email in usuarios_db and usuarios_db[email]["senha"] == hash_senha(senha):
                st.session_state.logado = True
                st.session_state.usuario = email
                st.success("Acesso liberado")
                st.rerun()
            else:
                st.error("Credenciais inválidas")

    # CADASTRO
    elif opcao == "Criar conta":
        novo_email = st.text_input("Novo email")
        nova_senha = st.text_input("Nova senha", type="password")

        if st.button("Cadastrar"):
            if novo_email in usuarios_db:
                st.warning("Usuário já existe")
            else:
                usuarios_db[novo_email] = {
                    "senha": hash_senha(nova_senha),
                    "premium": False
                }
                salvar_usuarios(usuarios_db)
                st.success("Conta criada com sucesso")

    # RECUPERAR
    elif opcao == "Recuperar senha":
        email_rec = st.text_input("Email")

        if st.button("Recuperar"):
            if email_rec in usuarios_db:
                st.info("Senha protegida. Crie uma nova conta ou redefina manualmente.")
            else:
                st.error("Email não encontrado")

    st.stop()

# =========================
# APP
# =========================
st.title("🛡️ Escudo Digital IA")
st.caption("Proteção inteligente contra golpes digitais")

st.markdown("### 🚨 Analise mensagens suspeitas em segundos")

# =========================
# PREMIUM
# =========================
st.subheader("💎 Premium")
st.code("13996469617")

st.success("Acesso avançado ativo")

# =========================
# ANALISE
# =========================
st.subheader("🔍 Central de Análise")
texto = st.text_area("Cole uma mensagem suspeita")

if st.button("🚀 Analisar"):
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
    texto_img = pytesseract.image_to_string(Image.open(img))
    st.text_area("Texto detectado", texto_img)

    if st.button("🔎 Analisar imagem"):
        st.success(analisar_texto(texto_img))

# =========================
# OSINT
# =========================
st.subheader("🌍 OSINT - Inteligência de IP")

ip = st.text_input("Digite um IP")

if st.button("🌐 Consultar OSINT"):
    if ip:
        st.info(consultar_ip(ip))

# =========================
# SOC
# =========================
st.subheader("📊 Painel SOC")

col1, col2, col3 = st.columns(3)

col1.metric("Eventos", st.session_state.eventos)
col2.metric("Suspeitos", st.session_state.suspeitos)
col3.metric("Alertas", st.session_state.alertas)

if st.session_state.alertas > 3:
    st.error("🚨 Alto risco detectado")
elif st.session_state.alertas > 0:
    st.warning("⚠️ Atividade suspeita")
else:
    st.success("🟢 Ambiente seguro")

# =========================
# ADMIN
# =========================
st.subheader("🔧 Administração")

usuario = st.session_state.usuario

if usuario in usuarios_db:
    st.info(f"👤 {usuario}")
    st.write(f"Premium: {'Ativo' if usuarios_db[usuario]['premium'] else 'Inativo'}")

if st.button("Ativar Premium"):
    usuarios_db[usuario]["premium"] = True
    salvar_usuarios(usuarios_db)
    st.success("Premium ativado")

if st.button("Sair"):
    st.session_state.logado = False
    st.rerun()

# =========================
# USUÁRIOS
# =========================
st.subheader("👥 Usuários")

for u in usuarios_db:
    status = "🟢 Premium" if usuarios_db[u]["premium"] else "⚪ Free"
    st.write(f"{u} — {status}")
