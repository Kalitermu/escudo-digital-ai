# =========================================================
# 🔐 SEGURANÇA
# =========================================================

import hashlib

ADMIN_EMAIL = "admin@escudo.com"

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def is_admin():
    return (
        st.session_state.logado and 
        st.session_state.email_usuario == ADMIN_EMAIL
    )

# =========================================================
# LOGIN
# =========================================================

st.sidebar.title("👤 Conta")

opcao = st.sidebar.selectbox(
    "Escolha uma opção",
    ["Entrar", "Criar conta", "Recuperar senha"]
)

# ==========================
# LOGIN
# ==========================

if opcao == "Entrar":
    email_login = st.sidebar.text_input("Email")
    senha_login = st.sidebar.text_input("Senha", type="password")

    if st.sidebar.button("Entrar"):
        if email_login in usuarios:
            if usuarios[email_login]["senha"] == hash_senha(senha_login):
                st.session_state.logado = True
                st.session_state.email_usuario = email_login
                st.sidebar.success("✅ Login realizado")
                st.rerun()
            else:
                st.sidebar.error("Senha incorreta")
        else:
            st.sidebar.error("Conta não encontrada")

# ==========================
# CRIAR CONTA
# ==========================

elif opcao == "Criar conta":
    novo_email = st.sidebar.text_input("Novo email")
    nova_senha = st.sidebar.text_input("Nova senha", type="password")

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

            st.sidebar.success("✅ Conta criada com sucesso!")
            st.rerun()

# ==========================
# RECUPERAR SENHA
# ==========================

elif opcao == "Recuperar senha":
    email_rec = st.sidebar.text_input("Email")
    nova_senha = st.sidebar.text_input("Nova senha", type="password")

    if st.sidebar.button("Redefinir senha"):
        if email_rec in usuarios:
            usuarios[email_rec]["senha"] = hash_senha(nova_senha)
            salvar_json(USERS_FILE, usuarios)
            st.sidebar.success("🔑 Senha redefinida!")
        else:
            st.sidebar.error("Email não encontrado")

# ==========================
# STATUS USUÁRIO
# ==========================

if st.session_state.logado:
    st.sidebar.success(f"👤 {st.session_state.email_usuario}")

    if premium_ativo():
        st.sidebar.success("💎 Premium ativo")
    else:
        st.sidebar.info(f"Análises grátis restantes: {uso_restante()}")

    st.sidebar.info("💳 Após pagamento, envie comprovante para ativação.")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.session_state.email_usuario = ""
        st.session_state.premium_demo = False
        st.rerun()
else:
    st.sidebar.info("Entre ou crie uma conta para usar o sistema.")

# =========================================================
# 🛠️ PAINEL ADMIN
# =========================================================

if is_admin():
    st.sidebar.markdown("## 🔧 Admin")

    pagina_admin = st.sidebar.selectbox(
        "Painel Admin",
        ["Usuários", "Controle Premium", "Resetar Senha", "Excluir Usuário"]
    )

    # ==========================
    # LISTAR USUÁRIOS
    # ==========================
    if pagina_admin == "Usuários":
        st.title("👥 Usuários cadastrados")

        if usuarios:
            lista = []
            for email, dados in usuarios.items():
                lista.append({
                    "Email": email,
                    "Uso": dados.get("uso", 0),
                    "Premium": dados.get("premium", False)
                })

            df_users = pd.DataFrame(lista)
            st.dataframe(df_users, use_container_width=True)
        else:
            st.info("Nenhum usuário cadastrado")

    # ==========================
    # CONTROLE PREMIUM
    # ==========================
    elif pagina_admin == "Controle Premium":
        st.title("💎 Gerenciar Premium")

        email_sel = st.selectbox("Selecionar usuário", list(usuarios.keys()))

        if email_sel:
            dados = usuarios[email_sel]

            st.write(f"Usuário: {email_sel}")
            st.write(f"Uso: {dados.get('uso', 0)}")
            st.write(f"Premium atual: {dados.get('premium', False)}")

            if st.button("✅ Ativar Premium"):
                usuarios[email_sel]["premium"] = True
                salvar_json(USERS_FILE, usuarios)
                st.success("Premium ativado!")

            if st.button("❌ Remover Premium"):
                usuarios[email_sel]["premium"] = False
                salvar_json(USERS_FILE, usuarios)
                st.warning("Premium removido!")

    # ==========================
    # RESET SENHA
    # ==========================
    elif pagina_admin == "Resetar Senha":
        st.title("🔑 Resetar senha")

        email_reset = st.selectbox("Usuário", list(usuarios.keys()))
        nova_senha = st.text_input("Nova senha", type="password")

        if st.button("Resetar"):
            usuarios[email_reset]["senha"] = hash_senha(nova_senha)
            salvar_json(USERS_FILE, usuarios)
            st.success("Senha atualizada!")

    # ==========================
    # EXCLUIR USUÁRIO
    # ==========================
    elif pagina_admin == "Excluir Usuário":
        st.title("🗑️ Excluir usuário")

        email_del = st.selectbox("Usuário", list(usuarios.keys()))

        if st.button("Excluir usuário"):
            if email_del == ADMIN_EMAIL:
                st.error("Não pode excluir admin")
            else:
                usuarios.pop(email_del)
                salvar_json(USERS_FILE, usuarios)
                st.success("Usuário removido!")

    st.divider()
