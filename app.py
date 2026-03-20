import streamlit as st
import os
from openai import OpenAI
from PIL import Image
import pytesseract

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
# IA + OFFLINE (MELHORADO)
# =========================
def analisar_texto(texto):
    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
Você é especialista em fraudes digitais (SOC).

Responda:

🔎 Risco:
📊 Score:
⚠️ Motivo:
💡 Recomendação:
"""
                },
                {"role": "user", "content": texto}
            ]
        )

        resultado = resposta.choices[0].message.content.strip()

        st.session_state.eventos += 1

        if "ALTO" in resultado:
            st.session_state.alertas += 1

        return resultado

    except:
        # 🔥 MODO OFFLINE INTELIGENTE
        texto_lower = texto.lower()

        risco = "BAIXO"
        score = 10
        motivos = []

        if "pix" in texto_lower:
            risco = "ALTO"
            score = 90
            motivos.append("Pedido de PIX")

        if "urgente" in texto_lower:
            risco = "ALTO"
            score = max(score, 85)
            motivos.append("Urgência")

        if "senha" in texto_lower or "código" in texto_lower:
            risco = "ALTO"
            score = 95
            motivos.append("Solicitação de dados sensíveis")

        if "link" in texto_lower:
            risco = "MÉDIO"
            score = max(score, 60)
            motivos.append("Link suspeito")

        if any(p in texto_lower for p in ["inss","benefício"]):
            risco = "ALTO"
            score = 92
            motivos.append("Possível golpe INSS")

        st.session_state.eventos += 1

        if risco == "ALTO":
            st.session_state.alertas += 1

        return f"""
🔎 Risco: {risco}
📊 Score: {score}
⚠️ Motivo: {', '.join(motivos) if motivos else 'Nenhum forte indício'}
💡 Recomendação: Não envie dados e confirme a origem
"""

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
            if novo_email and nova_senha:
                st.session_state.usuarios[novo_email] = {
                    "senha": nova_senha,
                    "premium": False
                }
                st.success("Conta criada!")

    elif opcao == "Esqueci senha":
        email_reset = st.text_input("Digite seu email")

        if st.button("Recuperar"):
            if email_reset in st.session_state.usuarios:
                st.success("Recuperação enviada (simulação)")
            else:
                st.error("Email não encontrado")

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
        st.success(analisar_texto(texto))

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
# SOC
# =========================
st.subheader("📊 SOC")

st.metric("Eventos", st.session_state.eventos)
st.metric("Suspeitos", st.session_state.suspeitos)
st.metric("Alertas", st.session_state.alertas)

if st.session_state.alertas > 0:
    st.error("🔴 Ameaças detectadas")
else:
    st.success("🟢 Ambiente seguro")

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
    status = "✅" if st.session_state.usuarios[u]["premium"] else "❌"
    st.write(f"{u} | {status}")
