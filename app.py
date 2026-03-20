import streamlit as st
import hashlib
import json
import pandas as pd

# =========================
# CONFIG
# =========================
USERS_FILE = "usuarios.json"
ADMIN_EMAIL = "admin@escudo.com"

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
# SIDEBAR LOGIN
# =========================
st.sidebar.title("👤 Conta")

opcao = st.sidebar.selectbox(
    "Escolha uma opção",
    ["Entrar", "Criar conta", "Recuperar senha"]
)

# =========================
# LOGIN
# =========================
if opcao == "Entrar":
    email_login = st.sidebar.text_input("Email", key="login_email")
    senha_login = st.sidebar.text_input("Senha", type="password", key="login_senha")

    if st.sidebar.button("Entrar"):
        if not email_login or not senha_login:
            st.sidebar.warning("Preencha todos os campos")
        elif email_login in usuarios:
            if usuarios[email_login]["senha"] == hash_senha(senha_login):
                st.session_state.logado = True
                st.session_state.email_usuario = email_login
                st.sidebar.success("✅ Login realizado")
                st.rerun()
            else:
                st.sidebar.error("Senha incorreta")
        else:
            st.sidebar.error("Conta não encontrada")

# =========================
# CRIAR CONTA
# =========================
elif opcao == "Criar conta":
    novo_email = st.sidebar.text_input("Novo email", key="novo_email")
    nova_senha = st.sidebar.text_input("Nova senha", type="password", key="nova_senha")

    if st.sidebar.button("Criar conta"):
        if not novo_email or not nova_senha:
            st.sidebar.warning("Preencha todos os campos")

        elif novo_email == ADMIN_EMAIL:
            st.sidebar.error("Email reservado")

        elif novo_email in usuarios:
            st.sidebar.warning("Conta já existe")

        else:
            usuarios[novo_email] = {
                "senha": hash_senha(nova_senha),
                "uso": 0,
                "premium": False
            }
            salvar_json(USERS_FILE, usuarios)

            st.session_state.logado = True
            st.session_state.email_usuario = novo_email

            st.sidebar.success("✅ Conta criada!")
            st.rerun()

# =========================
# RECUPERAR SENHA
# =========================
elif opcao == "Recuperar senha":
    email_rec = st.sidebar.text_input("Email", key="rec_email")
    nova_senha = st.sidebar.text_input("Nova senha", type="password", key="rec_senha")

    if st.sidebar.button("Redefinir senha"):
        if email_rec in usuarios:
            usuarios[email_rec]["senha"] = hash_senha(nova_senha)
            salvar_json(USERS_FILE, usuarios)
            st.sidebar.success("🔑 Senha atualizada!")
        else:
            st.sidebar.error("Email não encontrado")

# =========================
# STATUS
# =========================
if st.session_state.logado:
    st.sidebar.success(f"👤 {st.session_state.email_usuario}")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.session_state.email_usuario = ""
        st.rerun()
else:
    st.sidebar.info("Entre ou crie uma conta")

# =========================
# PAINEL ADMIN
# =========================
if is_admin():
    st.sidebar.markdown("## 🔧 Admin")

    pagina = st.sidebar.selectbox(
        "Painel",
        ["Usuários", "Premium", "Resetar Senha", "Excluir"]
    )

    # LISTAR
    if pagina == "Usuários":
        st.title("👥 Usuários")

        if usuarios:
            lista = []
            for email, dados in usuarios.items():
                lista.append({
                    "Email": email,
                    "Uso": dados.get("uso", 0),
                    "Premium": dados.get("premium", False)
                })

            st.dataframe(pd.DataFrame(lista))
        else:
            st.info("Nenhum usuário")

    # PREMIUM
    elif pagina == "Premium":
        st.title("💎 Premium")

        email_sel = st.selectbox("Usuário", list(usuarios.keys()))

        if st.button("Ativar"):
            usuarios[email_sel]["premium"] = True
            salvar_json(USERS_FILE, usuarios)
            st.success("Ativado")

        if st.button("Remover"):
            usuarios[email_sel]["premium"] = False
            salvar_json(USERS_FILE, usuarios)
            st.warning("Removido")

    # RESET
    elif pagina == "Resetar Senha":
        st.title("🔑 Reset")

        email = st.selectbox("Usuário", list(usuarios.keys()))
        nova = st.text_input("Nova senha", type="password")

        if st.button("Resetar"):
            usuarios[email]["senha"] = hash_senha(nova)
            salvar_json(USERS_FILE, usuarios)
            st.success("Atualizado")

    # EXCLUIR
    elif pagina == "Excluir":
        st.title("🗑️ Excluir")

        email = st.selectbox("Usuário", list(usuarios.keys()))

        if st.button("Excluir"):
            if email == ADMIN_EMAIL:
                st.error("Não pode excluir admin")
            else:
                usuarios.pop(email)
                salvar_json(USERS_FILE, usuarios)
                st.success("Removido")

# =========================
# HOME
# =========================
st.title("🛡️ Escudo Digital IA")

if not st.session_state.logado:
    st.warning("Faça login para usar o sistema")
else:
    st.success("Sistema ativo 🚀")
