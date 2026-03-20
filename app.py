import streamlit as st
import json
import os
from openai import OpenAI
from PIL import Image
import pytesseract

# =========================
# CONFIG IA
# =========================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# BANCO SIMPLES
# =========================
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {
        "joseluizariel@gmail.com": {"senha": "123", "premium": True}
    }

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
# FUNÇÃO IA
# =========================
def analisar_texto(texto):
    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
Você é um especialista em cibersegurança e fraudes digitais (SOC).

Detecte golpes e classifique:

- Risco: BAIXO, MÉDIO ou ALTO
- Score: 0 a 100

Analise:
- Urgência
- PIX / dinheiro
- Links
- Falsa identidade
- Pressão psicológica

Responda assim:

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

        if any(p in texto.lower() for p in ["pix", "urgente", "senha", "código"]):
            st.session_state.suspeitos += 1

        return resultado

    except Exception as e:
        return f"Erro IA: {e}"

# =========================
# LOGIN
# =========================
if not st.session_state.logado:
    st.title("🔐 Login Escudo Digital")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if email in st.session_state.usuarios and st.session_state.usuarios[email]["senha"] == senha:
            st.session_state.logado = True
            st.session_state.usuario = email
            st.success("Login realizado")
        else:
            st.error("Login inválido")

    st.stop()

# =========================
# APP
# =========================
st.title("🛡️ Escudo Digital IA")
st.caption("Proteção contra golpes digitais")

st.subheader("💎 Premium")
st.code("13996469617")
st.link_button("📲 Enviar comprovante", "https://wa.me/5513996469617?text=paguei%20premium")

# =========================
# ANÁLISE
# =========================
st.subheader("🔍 Central de Análise")
texto = st.text_area("Cole mensagem suspeita")

if st.button("Analisar"):
    if texto:
        resultado = analisar_texto(texto)
        st.success(resultado)

# =========================
# PRINT
# =========================
st.subheader("📷 Analisar print de golpe")
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
st.subheader("📧 Analisar email")
st.text_area("Cole email")

st.subheader("📱 Golpe WhatsApp")
st.text_area("Cole conversa")

st.subheader("👴 Golpe contra idoso")
st.text_area("Mensagem INSS")

# =========================
# BIBLIOTECA
# =========================
st.subheader("📚 Biblioteca de golpes")
st.write("- 💸 golpe_pix")
st.write("- 🏦 emprestimo_falso")
st.write("- 🔐 phishing")
st.write("- ⚠️ extorsao")
st.write("- 📱 golpe_whatsapp")
st.write("- 👴 golpe_idoso")

# =========================
# SOC
# =========================
st.subheader("📊 Painel SOC")

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

usuario = st.session_state.usuario
premium = st.session_state.usuarios[usuario]["premium"]

st.write(f"Usuário: {usuario}")
st.write(f"Premium: {'✅ Ativo' if premium else '❌ Não'}")

if st.button("Ativar Premium"):
    st.session_state.usuarios[usuario]["premium"] = True
    st.success("Premium ativado")

if st.button("Remover Premium"):
    st.session_state.usuarios[usuario]["premium"] = False

if st.button("Sair"):
    st.session_state.logado = False
    st.experimental_rerun()

# =========================
# USUÁRIOS
# =========================
st.subheader("👥 Usuários cadastrados")

for u in st.session_state.usuarios:
    status = "✅" if st.session_state.usuarios[u]["premium"] else "❌"
    st.write(f"{u} | Premium: {status}")
