import streamlit as st

# CONFIG
st.set_page_config(page_title="Escudo Digital IA", layout="centered")

# ===== BANCO SIMPLES =====
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {
        "joseluizariel@gmail.com": {
            "senha": "123",
            "premium": True
        }
    }

if "logado" not in st.session_state:
    st.session_state.logado = False

# ===== LOGIN / CADASTRO =====
if not st.session_state.logado:
    st.title("🔐 Login Escudo Digital")

    opcao = st.selectbox("Escolha", ["Login", "Criar conta", "Esqueci a senha"])

    # LOGIN
    if opcao == "Login":
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if email in st.session_state.usuarios and st.session_state.usuarios[email]["senha"] == senha:
                st.session_state.logado = True
                st.session_state.email = email
                st.rerun()
            else:
                st.error("Login inválido")

    # CADASTRO
    if opcao == "Criar conta":
        novo_email = st.text_input("Novo email")
        nova_senha = st.text_input("Nova senha", type="password")

        if st.button("Cadastrar"):
            st.session_state.usuarios[novo_email] = {
                "senha": nova_senha,
                "premium": False
            }
            st.success("Conta criada!")

    # RECUPERAR SENHA
    if opcao == "Esqueci a senha":
        email_reset = st.text_input("Digite seu email")

        if st.button("Recuperar"):
            if email_reset in st.session_state.usuarios:
                st.warning(f"Sua senha é: {st.session_state.usuarios[email_reset]['senha']}")
            else:
                st.error("Email não encontrado")

    st.stop()

# ===== APP =====
st.title("🛡️ Escudo Digital IA")
st.caption("Proteção contra golpes digitais")

usuario = st.session_state.email
premium = st.session_state.usuarios[usuario]["premium"]

# ===== PREMIUM =====
st.subheader("💎 Premium")
st.code("13996469617")
st.link_button("📲 Enviar comprovante", "https://wa.me/5513996469617?text=paguei%20premium")

# ===== ANALISE =====
st.subheader("🔍 Central de Análise")

texto = st.text_area("Cole mensagem suspeita")

def analisar(msg):
    risco = 0
    palavras = []

    if "urgente" in msg.lower():
        risco += 30
        palavras.append("Urgência")

    if "pix" in msg.lower():
        risco += 30
        palavras.append("PIX")

    if "inss" in msg.lower():
        risco += 30
        palavras.append("INSS")

    return risco, palavras

if st.button("🔎 Analisar agora"):
    risco, palavras = analisar(texto)

    if risco == 0:
        st.success("🟢 Baixo risco")
    elif risco < 60:
        st.warning(f"🟡 Risco médio ({risco}%)")
    else:
        st.error(f"🔴 Alto risco ({risco}%)")

    st.write("Detectado:", palavras)

# ===== IMAGEM =====
st.subheader("📷 Analisar print de golpe")
img = st.file_uploader("Envie imagem", type=["png","jpg","jpeg"])

if img:
    st.image(img)

# ===== EMAIL =====
st.subheader("📧 Analisar email")
email_txt = st.text_area("Cole email")

if st.button("Analisar email"):
    st.info("Análise simulada feita")

# ===== WHATSAPP =====
st.subheader("📱 Golpe WhatsApp")
zap = st.text_area("Cole conversa")

if st.button("Analisar WhatsApp"):
    st.info("Análise simulada")

# ===== IDOSO =====
st.subheader("👴 Golpe contra idoso")
idoso = st.text_area("Mensagem INSS")

if st.button("Analisar INSS"):
    if "inss" in idoso.lower():
        st.error("⚠️ Possível golpe do INSS")
    else:
        st.success("Sem risco")

# ===== BIBLIOTECA =====
st.subheader("📚 Biblioteca de golpes")

st.markdown("""
- 💸 golpe_pix — pedido urgente de dinheiro  
- 🏦 emprestimo_falso — crédito fácil  
- 🔐 phishing — roubo de senha  
- ⚠️ extorsao — ameaça  
- 📱 golpe_whatsapp — troca de número  
- 👴 golpe_idoso — INSS  
""")

# ===== SOC =====
st.subheader("📊 Painel SOC")

st.metric("Eventos", 0)
st.metric("Suspeitos", 0)
st.metric("Alertas", 0)

st.success("🟢 Ambiente seguro")

# ===== ADMIN =====
st.subheader("🔧 Admin")
st.write("Usuário:", usuario)
st.write("Premium:", "✅ Ativo" if premium else "❌ Não")

if st.button("Ativar Premium"):
    st.session_state.usuarios[usuario]["premium"] = True
    st.success("Premium ativado")

if st.button("Remover Premium"):
    st.session_state.usuarios[usuario]["premium"] = False
    st.warning("Premium removido")

# ===== LOGOUT =====
if st.button("Sair"):
    st.session_state.logado = False
    st.rerun()
