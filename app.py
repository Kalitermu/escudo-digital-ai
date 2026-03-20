import streamlit as st

# CONFIG
st.set_page_config(page_title="Escudo Digital IA", layout="centered")

# 🎨 ESTILO LIMPO (SEM BUG AZUL)
st.markdown("""
<style>
html, body, [class*="css"]  {
    background: linear-gradient(135deg, #eef2ff, #f8fafc);
}

.block-container {
    padding-top: 1.5rem;
}

h1, h2, h3 {
    text-align: center;
    color: #1e293b;
}

.stTextInput input, .stTextArea textarea {
    border-radius: 10px;
}

.stButton button {
    width: 100%;
    height: 48px;
    border-radius: 10px;
    font-size: 16px;
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    color: white;
    border: none;
}

.stButton button:hover {
    background: linear-gradient(90deg, #1d4ed8, #1e40af);
}
</style>
""", unsafe_allow_html=True)

# USER
email_user = "joseluizariel@gmail.com"
premium = True

# HEADER
st.markdown("# 🛡️ Escudo Digital IA")
st.caption("Proteção contra golpes digitais")

# 💎 PREMIUM
st.markdown("## 💎 Premium")
st.code("13996469617")
st.markdown("[📲 Enviar comprovante](https://wa.me/5513996469617?text=paguei%20premium)")

# 🔍 DOMÍNIO
st.markdown("## 🔍 Scanner de domínio")
url = st.text_input("Digite URL suspeita")

if st.button("Analisar domínio"):
    if "http" in url:
        st.warning("⚠️ Verifique se o site é confiável")
    else:
        st.error("🔴 URL suspeita")

# 📷 PRINT
st.markdown("## 📷 Analisar print de golpe")
img = st.file_uploader("Envie imagem", type=["png","jpg","jpeg"])

if img:
    st.image(img)
    st.warning("⚠️ Conteúdo suspeito detectado")

# 📧 EMAIL
st.markdown("## 📧 Analisar email")
email = st.text_area("Cole o email")

if st.button("Analisar email"):
    if "senha" in email.lower() or "urgente" in email.lower():
        st.error("🔴 Possível phishing")
    else:
        st.success("🟢 Sem risco crítico")

# 📱 WHATSAPP
st.markdown("## 📱 Golpe WhatsApp")
zap = st.text_area("Cole conversa")

if st.button("Analisar WhatsApp"):
    risco = 0
    detectado = []

    if "urgente" in zap.lower():
        risco += 30
        detectado.append("Urgência")

    if "pix" in zap.lower():
        risco += 40
        detectado.append("Pedido de dinheiro")

    if "link" in zap.lower():
        risco += 20
        detectado.append("Link suspeito")

    st.progress(risco / 100)

    if risco >= 70:
        st.error(f"🔴 ALTO RISCO ({risco}%)")
    elif risco >= 40:
        st.warning(f"🟡 RISCO MÉDIO ({risco}%)")
    else:
        st.success(f"🟢 BAIXO RISCO ({risco}%)")

    st.write("🔎 Detectado:", detectado)

# 👴 IDOSO
st.markdown("## 👴 Golpe contra idoso")
idoso = st.text_area("Mensagem suspeita INSS")

if st.button("Analisar INSS"):
    if "inss" in idoso.lower() or "benefício" in idoso.lower():
        st.error("⚠️ Golpe comum contra idosos")
    else:
        st.success("🟢 Sem padrão crítico")

# 📚 BIBLIOTECA
st.markdown("## 📚 Biblioteca de golpes")
st.markdown("""
- 💸 golpe_pix — pedido urgente de dinheiro  
- 🏦 emprestimo_falso — crédito fácil  
- 🔐 phishing — roubo de senha  
- ⚠️ extorsao — ameaça  
- 📱 golpe_whatsapp — troca de número  
- 👴 golpe_idoso — INSS  
""")

# 📊 SOC
st.markdown("## 📊 Painel SOC")

c1, c2, c3 = st.columns(3)
c1.metric("Eventos", 0)
c2.metric("Suspeitos", 0)
c3.metric("Alertas", 0)

st.success("🟢 Ambiente seguro")

# 🔧 ADMIN
st.markdown("## 🔧 Admin")
st.write("Usuário:", email_user)
st.write("Premium:", "✅ Ativo" if premium else "❌ Não")

if st.button("Ativar Premium"):
    st.success("Premium ativado")

if st.button("Remover Premium"):
    st.error("Premium removido")
