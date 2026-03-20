import streamlit as st
import hashlib
import json
from datetime import datetime, timedelta

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Escudo Digital IA", layout="wide")

USERS_FILE = "usuarios.json"
ADMIN_EMAIL = "admin@escudo.com"
LIMITE_GRATIS = 7

WHATSAPP_LINK = "https://wa.me/5513996469617?text=Olá,%20acabei%20de%20pagar%20o%20Escudo%20Digital%20Premium.%20Segue%20o%20comprovante."

# =========================
# JSON
# =========================
def carregar_json(nome, padrao):
    try:
        with open(nome, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return padrao

def salvar_json(nome, dados):
    with open(nome, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2)

usuarios = carregar_json(USERS_FILE, {})

# =========================
# SESSÃO
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False

if "email_usuario" not in st.session_state:
    st.session_state.email_usuario = ""

# =========================
# SEGURANÇA
# =========================
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def is_admin():
    return (
        st.session_state.logado and
        st.session_state.email_usuario == ADMIN_EMAIL
    )

# =========================
# PREMIUM
# =========================
def premium_ativo():
    if not st.session_state.logado:
        return False

    user = usuarios.get(st.session_state.email_usuario)

    if user.get("premium"):
        exp = user.get("premium_expira")
        if exp:
            return datetime.now() <= datetime.strptime(exp, "%Y-%m-%d")
        return True

    return False

def uso_restante():
    user = usuarios.get(st.session_state.email_usuario)
    return max(0, LIMITE_GRATIS - user.get("uso", 0))

# =========================
# SIDEBAR
# =========================
st.sidebar.title("👤 Conta")

opcao = st.sidebar.selectbox(
    "Escolha",
    ["Entrar", "Criar conta", "Recuperar senha"]
)

# LOGIN
if opcao == "Entrar":
    email = st.sidebar.text_input("Email")
    senha = st.sidebar.text_input("Senha", type="password")

    if st.sidebar.button("Entrar"):
        if email in usuarios:
            if usuarios[email]["senha"] == hash_senha(senha):
                st.session_state.logado = True
                st.session_state.email_usuario = email
                st.rerun()
            else:
                st.sidebar.error("Senha incorreta")
        else:
            st.sidebar.error("Conta não encontrada")

# CRIAR
elif opcao == "Criar conta":
    email = st.sidebar.text_input("Novo email")
    senha = st.sidebar.text_input("Nova senha", type="password")

    if st.sidebar.button("Criar"):
        if email == ADMIN_EMAIL:
            st.sidebar.error("Email reservado")
        else:
            usuarios[email] = {
                "senha": hash_senha(senha),
                "uso": 0,
                "premium": False
            }
            salvar_json(USERS_FILE, usuarios)
            st.sidebar.success("Conta criada!")

# RECUPERAR
elif opcao == "Recuperar senha":
    email = st.sidebar.text_input("Email")
    senha = st.sidebar.text_input("Nova senha", type="password")

    if st.sidebar.button("Resetar"):
        if email in usuarios:
            usuarios[email]["senha"] = hash_senha(senha)
            salvar_json(USERS_FILE, usuarios)
            st.sidebar.success("Senha atualizada")

# STATUS
if st.session_state.logado:
    st.sidebar.success(f"👤 {st.session_state.email_usuario}")

    if premium_ativo():
        st.sidebar.success("💎 Premium ativo")
    else:
        st.sidebar.info(f"Restam {uso_restante()} análises grátis")

        # BOTÃO WHATSAPP
        st.sidebar.info("💳 Após pagamento, envie o comprovante:")
        st.sidebar.markdown(f"[📲 Enviar comprovante]({WHATSAPP_LINK})")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.session_state.email_usuario = ""
        st.rerun()

# =========================
# ADMIN
# =========================
if is_admin():
    st.sidebar.markdown("## 🔧 Admin")

    pagina = st.sidebar.selectbox("Painel", ["Usuários", "Premium"])

    if pagina == "Usuários":
        st.write("### Usuários")
        st.write(usuarios)

    if pagina == "Premium":
        email = st.selectbox("Usuário", list(usuarios.keys()))

        if st.button("Ativar 30 dias"):
            usuarios[email]["premium"] = True
            usuarios[email]["premium_expira"] = (
                datetime.now() + timedelta(days=30)
            ).strftime("%Y-%m-%d")

            salvar_json(USERS_FILE, usuarios)
            st.success("Premium ativado")

# =========================
# APP
# =========================
st.title("🛡️ Escudo Digital IA")

if not st.session_state.logado:
    st.warning("Faça login para usar o sistema")

    st.markdown("### 💎 Plano Premium")
    st.write("Apenas R$ 9,90/mês")
    st.code("PIX AQUI")

else:
    if not premium_ativo() and uso_restante() <= 0:
        st.error("🚫 Limite atingido")
        st.stop()

    if st.button("🔎 Fazer análise"):
        usuarios[st.session_state.email_usuario]["uso"] += 1
        salvar_json(USERS_FILE, usuarios)

        st.success("Análise feita!")
