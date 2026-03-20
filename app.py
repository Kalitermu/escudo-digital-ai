import streamlit as st
import os
import requests
from openai import OpenAI
from PIL import Image
import pytesseract
import folium
from streamlit_folium import st_folium

# =========================
# 🎨 ESTILO (FUNDO AZUL)
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e3a8a);
    color: white;
}
h1, h2, h3, h4, h5 {
    color: #e0f2fe;
}
.stTextInput input, .stTextArea textarea {
    background-color: #1e293b;
    color: white;
}
.stButton button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# CONFIG IA
# =========================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# BANCO
# =========================
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {
        "joseluizariel@gmail.com": {"senha": "123", "premium": True}
    }

# =========================
# SESSÃO
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = None

# SOC
if "eventos" not in st.session_state:
    st.session_state.eventos = 0
if "alertas" not in st.session_state:
    st.session_state.alertas = 0
if "suspeitos" not in st.session_state:
    st.session_state.suspeitos = 0

# =========================
# IA + OFFLINE
# =========================
def analisar_texto(texto):
    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Analise golpes e classifique risco"},
                {"role": "user", "content": texto}
            ]
        )
        resultado = resposta.choices[0].message.content
        st.session_state.eventos += 1

        if "ALTO" in resultado:
            st.session_state.alertas += 1

        return resultado

    except:
        texto_lower = texto.lower()
        risco = "BAIXO"
        score = 10

        if "pix" in texto_lower:
            risco = "ALTO"; score = 90
        elif "urgente" in texto_lower:
            risco = "ALTO"; score = 85
        elif "senha" in texto_lower:
            risco = "ALTO"; score = 95
        elif "link" in texto_lower:
            risco = "MÉDIO"; score = 60

        st.session_state.eventos += 1

        if risco == "ALTO":
            st.session_state.alertas += 1

        return f"🔎 Risco: {risco}\n📊 Score: {score}"

# =========================
# OSINT REAL + MAPA
# =========================
def osint_ip(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()

        if res["status"] == "success":
            lat = res["lat"]
            lon = res["lon"]

            st.success("Resultado OSINT")
            st.write(f"🌍 País: {res['country']}")
            st.write(f"🏙️ Cidade: {res['city']}")
            st.write(f"📡 ISP: {res['isp']}")

            # MAPA
            mapa = folium.Map(location=[lat, lon], zoom_start=10)
            folium.Marker([lat, lon], tooltip="Localização").add_to(mapa)
            st_folium(mapa, width=300, height=300)

        else:
            st.error("IP não encontrado")

    except:
        st.error("Erro OSINT")

# =========================
# LOGIN / CADASTRO
# =========================
if not st.session_state.logado:

    st.title("🔐 Escudo Digital")

    opcao = st.selectbox("Escolha", ["Login", "Criar conta", "Esqueci senha"])

    if opcao == "Login":
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if email in st.session_state.usuarios and st.session_state.usuarios[email]["senha"] == senha:
                st.session_state.logado = True
                st.session_state.usuario = email
                st.rerun()
            else:
                st.error("Login inválido")

    elif opcao == "Criar conta":
        novo_email = st.text_input("Novo email")
        nova_senha = st.text_input("Nova senha", type="password")

        if st.button("Cadastrar"):
            st.session_state.usuarios[novo_email] = {
                "senha": nova_senha,
                "premium": False
            }
            st.success("Conta criada!")

    elif opcao == "Esqueci senha":
        email_reset = st.text_input("Digite seu email")

        if st.button("Recuperar"):
            st.success("Recuperação enviada (simulação)")

    st.stop()

# =========================
# APP
# =========================
st.title("🛡️ Escudo Digital IA")
st.caption("Proteção contra golpes digitais")

usuario = st.session_state.usuario
premium = st.session_state.usuarios[usuario]["premium"]

# PREMIUM
st.subheader("💎 Premium")
st.code("13996469617")
st.link_button("📲 Enviar comprovante", "https://wa.me/5513996469617")

# =========================
# CENTRAL
# =========================
st.subheader("🔍 Central de Análise")
texto = st.text_area("Cole mensagem suspeita")

if st.button("Analisar"):
    if texto:
        if premium:
            st.success(analisar_texto(texto))
        else:
            st.warning("🔒 Apenas Premium")

# =========================
# PRINT
# =========================
st.subheader("📷 Analisar print")
img = st.file_uploader("Envie imagem")

if img:
    imagem = Image.open(img)
    texto_img = pytesseract.image_to_string(imagem)
    st.text_area("Texto detectado", texto_img)

    if st.button("Analisar imagem"):
        st.success(analisar_texto(texto_img))

# =========================
# OSINT
# =========================
st.subheader("🌍 OSINT - Análise de IP")
ip_input = st.text_input("Digite IP")

if st.button("Consultar OSINT"):
    if ip_input:
        osint_ip(ip_input)

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
st.write("- golpe_pix")
st.write("- phishing")
st.write("- whatsapp")

# =========================
# SOC DASHBOARD
# =========================
st.subheader("📊 SOC")

col1, col2, col3 = st.columns(3)

col1.metric("Eventos", st.session_state.eventos)
col2.metric("Suspeitos", st.session_state.suspeitos)
col3.metric("Alertas", st.session_state.alertas)

if st.session_state.alertas > 3:
    st.error("🚨 Alto risco")
elif st.session_state.alertas > 0:
    st.warning("⚠️ Atenção")
else:
    st.success("🟢 Seguro")

# =========================
# ADMIN
# =========================
st.subheader("🔧 Admin")

st.write("Usuário:", usuario)
st.write("Premium:", "✅" if premium else "❌")

if st.button("Ativar Premium"):
    st.session_state.usuarios[usuario]["premium"] = True

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
    status = "🟢 Premium" if st.session_state.usuarios[u]["premium"] else "⚪ Free"
    st.write(f"{u} — {status}")
