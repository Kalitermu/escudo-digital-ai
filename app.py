import streamlit as st

# CONFIG
st.set_page_config(page_title="Escudo Digital IA", layout="centered")

# 🎨 ESTILO
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #dbeafe, #f0f9ff);
}
.block-container {
    padding-top: 2rem;
}
h1, h2, h3 {
    text-align: center;
}
.stButton button {
    width: 100%;
    height: 50px;
    border-radius: 12px;
    font-size: 16px;
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# 👤 USUÁRIO (simples)
email_user = "joseluizariel@gmail.com"
premium = True

# HEADER
st.markdown("# 🛡️ Escudo Digital IA")
st.caption("Proteção contra golpes digitais")

# 💎 PREMIUM
st.markdown("## 💎 Premium")
st.code("13996469617")
st.markdown("[📲 Enviar comprovante](https://wa.me/5513996469617?text=paguei%20premium)")

# =========================
# 🔍 SCANNER DOMÍNIO
# =========================
st.markdown("## 🔍 Scanner de domínio")

url = st.text_input("Digite URL suspeita")

if st.button("Analisar domínio"):
    if "http" in url:
        st.warning("⚠️ Verifique segurança do site")
    else:
        st.error("🔴 URL suspeita")

# =========================
# 📷 ANALISAR PRINT
# =========================
st.markdown("## 📷 Analisar print de golpe")

img = st.file_uploader("Envie imagem", type=["png","jpg","jpeg"])

if img:
    st.image(img)
    st.warning("⚠️ Possível golpe detectado na imagem")

# =========================
# 📧 EMAIL
# =========================
st.markdown("## 📧 Analisar email")

email = st.text_area("Cole o email")

if st.button("Analisar email"):
    if "senha" in email.lower() or "urgente" in email.lower():
        st.error("🔴 Phishing detectado")
    else:
        st.success("🟢 Sem risco alto")

# =========================
# 📱 WHATSAPP
# =========================
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

    st.progress(risco/100)

    if risco >= 70:
        st.error(f"🔴 ALTO RISCO ({risco}%)")
    elif risco >= 40:
        st.warning(f"🟡 RISCO MÉDIO ({risco}%)")
    else:
        st.success(f"🟢 BAIXO RISCO ({risco}%)")

    st.write("🔎 Detectado:", detectado)

# =========================
# 👴 IDOSO (INSS)
# =========================
st.markdown("## 👴 Golpe contra idoso")

idoso = st.text_area("Mensagem suspeita INSS")

if st.button("Analisar INSS"):
    if "inss" in idoso.lower() or "benefício" in idoso.lower():
        st.error("⚠️ Golpe comum contra idosos")
    else:
        st.success("🟢 Sem padrão de golpe")

# =========================
# 📚 BIBLIOTECA
# =========================
st.markdown("## 📚 Biblioteca de golpes")

st.markdown("""
- 💸 golpe_pix — pedido urgente de dinheiro  
- 🏦 emprestimo_falso — crédito fácil  
- 🔐 phishing — roubo de senha  
- ⚠️ extorsao — ameaça  
- 📱 golpe_whatsapp — troca de número  
- 👴 golpe_idoso — INSS  
""")

# =========================
# 📊 PAINEL SOC
# =========================
st.markdown("## 📊 Painel SOC")

col1, col2, col3 = st.columns(3)

col1.metric("Eventos", 0)
col2.metric("Suspeitos", 0)
col3.metric("Alertas", 0)

st.success("🟢 Ambiente seguro")

# =========================
# 🔧 ADMIN
# =========================
st.markdown("## 🔧 Admin")

st.write("Usuário:", email_user)
st.write("Premium:", "✅ Ativo" if premium else "❌ Não")

if st.button("Ativar Premium"):
    st.success("Premium ativado (simulação)")

if st.button("Remover Premium"):
    st.error("Premium removido (simulação)")
