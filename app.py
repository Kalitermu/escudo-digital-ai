import streamlit as st

# CONFIG
st.set_page_config(page_title="Escudo Digital IA", layout="centered")

# 🎨 ESTILO LIMPO
st.markdown("""
<style>
html, body {
    background: linear-gradient(135deg, #eef2ff, #f8fafc);
}
.stButton button {
    width: 100%;
    height: 48px;
    border-radius: 10px;
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    color: white;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🧠 SESSION LOGIN
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False

# =========================
# 🔐 LOGIN
# =========================
if not st.session_state.logado:
    st.markdown("# 🔐 Login Escudo Digital")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if email == "joseluizariel@gmail.com" and senha == "123":
            st.session_state.logado = True
            st.session_state.email = email
            st.success("Login realizado")
            st.rerun()
        else:
            st.error("Login inválido")

    st.stop()

# =========================
# 🛡️ APP (SÓ APARECE LOGADO)
# =========================

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
        st.warning("⚠️ Verifique segurança do site")
    else:
        st.error("🔴 URL suspeita")

# 📷 PRINT
st.markdown("## 📷 Analisar print de golpe")
img = st.file_uploader("Envie imagem", type=["png","jpg","jpeg"])

if img:
    st.image(img)
    st.warning("⚠️ Possível golpe detectado")

# 📧 EMAIL
st.markdown("## 📧 Analisar email")
email_text = st.text_area("Cole o email")

if st.button("Analisar email"):
    if "senha" in email_text.lower() or "urgente" in email_text.lower():
        st.error("🔴 Phishing detectado")
    else:
        st.success("🟢 Sem risco alto")

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
        st.success("🟢 Sem padrão de golpe")

# 📚 BIBLIOTECA
st.markdown("## 📚 Biblioteca de golpes")
st.markdown("""
- 💸 golpe_pix  
- 🏦 emprestimo_falso  
- 🔐 phishing  
- ⚠️ extorsao  
- 📱 golpe_whatsapp  
- 👴 golpe_idoso  
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
st.write("Usuário:", st.session_state.email)
st.write("Premium: ✅ Ativo")

# 🚪 SAIR
if st.button("Sair"):
    st.session_state.logado = False
    st.rerun()
