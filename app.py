import streamlit as st

st.set_page_config(page_title="Escudo Digital IA", layout="centered")

# ===== BANCO =====
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {
        "joseluizariel@gmail.com": {
            "senha": "123",
            "premium": True
        }
    }

if "logado" not in st.session_state:
    st.session_state.logado = False

# ===== SOC =====
if "eventos" not in st.session_state:
    st.session_state.eventos = 0
    st.session_state.suspeitos = 0
    st.session_state.alertas = 0

# ===== LOGIN =====
if not st.session_state.logado:
    st.title("🔐 Login Escudo Digital")

    opcao = st.selectbox("Escolha", ["Login", "Criar conta", "Esqueci a senha"])

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

    if opcao == "Criar conta":
        novo_email = st.text_input("Novo email")
        nova_senha = st.text_input("Nova senha", type="password")

        if st.button("Cadastrar"):
            st.session_state.usuarios[novo_email] = {
                "senha": nova_senha,
                "premium": False
            }
            st.success("Conta criada!")

    if opcao == "Esqueci a senha":
        email_reset = st.text_input("Digite seu email")

        if st.button("Recuperar"):
            if email_reset in st.session_state.usuarios:
                st.success("Link de recuperação enviado (simulação)")
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

# ===== IA DE ANÁLISE =====
def analisar(msg):
    risco = 0
    palavras = []

    golpes = {
        "urgente": 30,
        "pix": 30,
        "inss": 40,
        "taxa": 20,
        "clique": 15,
        "link": 20,
        "senha": 40,
        "bloqueado": 30,
        "whatsapp": 20
    }

    for palavra, peso in golpes.items():
        if palavra in msg.lower():
            risco += peso
            palavras.append(palavra)

    return min(risco, 100), palavras

# ===== ANALISE =====
st.subheader("🔍 Central de Análise")
texto = st.text_area("Cole mensagem suspeita")

if st.button("🔎 Analisar agora"):
    risco, palavras = analisar(texto)

    st.session_state.eventos += 1

    if risco > 50:
        st.session_state.suspeitos += 1

    if risco > 70:
        st.session_state.alertas += 1

    st.progress(risco / 100)

    if risco < 40:
        st.success("🟢 Baixo risco")
    elif risco < 70:
        st.warning(f"🟡 Risco médio ({risco}%)")
    else:
        st.error(f"🔴 Alto risco ({risco}%)")

    st.write("Detectado:", palavras)

# ===== IMAGEM =====
st.subheader("📷 Analisar print de golpe")
img = st.file_uploader("Envie imagem", type=["png","jpg","jpeg"])

if img:
    st.image(img)
    st.warning("⚠️ Possível golpe detectado na imagem (simulação IA)")

# ===== EMAIL =====
st.subheader("📧 Analisar email")
email_txt = st.text_area("Cole email")

if st.button("Analisar email"):
    st.session_state.eventos += 1
    st.warning("⚠️ Email suspeito detectado (simulação)")

# ===== WHATSAPP =====
st.subheader("📱 Golpe WhatsApp")
zap = st.text_area("Cole conversa")

if st.button("Analisar WhatsApp"):
    st.session_state.eventos += 1
    st.warning("⚠️ Possível golpe WhatsApp")

# ===== IDOSO =====
st.subheader("👴 Golpe contra idoso")
idoso = st.text_area("Mensagem INSS")

if st.button("Analisar INSS"):
    st.session_state.eventos += 1
    if "inss" in idoso.lower():
        st.session_state.alertas += 1
        st.error("⚠️ Golpe do INSS detectado")
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

st.metric("Eventos", st.session_state.eventos)
st.metric("Suspeitos", st.session_state.suspeitos)
st.metric("Alertas", st.session_state.alertas)

if st.session_state.alertas == 0:
    st.success("🟢 Ambiente seguro")
else:
    st.error("🔴 Ameaças detectadas")

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
