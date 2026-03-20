import streamlit as st
import hashlib
import json
import pandas as pd
from datetime import datetime, timedelta

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Escudo Digital IA", layout="wide")

USERS_FILE = "usuarios.json"
HIST_FILE = "historico.json"
ADMIN_EMAIL = "admin@escudo.com"
LIMITE_GRATIS = 7
PRECO_PREMIUM = "R$ 9,90/mês"
PIX_CODE = "00020126580014BR.GOV.BCB.PIX01365cecf979-d86a-4b71-9f03-a807d013e28a52040000530398654049.905802BR5915Ariel Jose Luiz6009SAO PAULO62140510tYrHuV1cyX63044599"

# =========================================================
# ESTILO
# =========================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#eef4ff,#d9e8ff);
}
.bloco {
    background: white;
    border: 1px solid #dbeafe;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 14px;
}
.premium {
    background: #ecfeff;
    border: 1px solid #67e8f9;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 14px;
}
.admin {
    background: #fff7ed;
    border: 1px solid #fdba74;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 14px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# JSON
# =========================================================
def carregar_json(nome, padrao):
    try:
        with open(nome, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return padrao

def salvar_json(nome, dados):
    with open(nome, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

usuarios = carregar_json(USERS_FILE, {})
historico = carregar_json(HIST_FILE, [])

# =========================================================
# SESSÃO
# =========================================================
if "logado" not in st.session_state:
    st.session_state.logado = False

if "email_usuario" not in st.session_state:
    st.session_state.email_usuario = ""

# =========================================================
# SEGURANÇA
# =========================================================
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def is_admin():
    return (
        st.session_state.get("logado", False)
        and st.session_state.get("email_usuario", "") == ADMIN_EMAIL
    )

# =========================================================
# USUÁRIO
# =========================================================
def usuario_logado():
    if not st.session_state.logado:
        return None
    return usuarios.get(st.session_state.email_usuario)

def premium_ativo():
    user = usuario_logado()
    if not user:
        return False

    if not user.get("premium", False):
        return False

    expira = user.get("premium_expira")
    if not expira:
        return True

    try:
        data_exp = datetime.strptime(expira, "%Y-%m-%d")
        return datetime.now() <= data_exp
    except Exception:
        return False

def uso_restante():
    user = usuario_logado()
    if not user:
        return LIMITE_GRATIS
    return max(0, LIMITE_GRATIS - user.get("uso", 0))

def limite_atingido():
    if premium_ativo():
        return False
    return uso_restante() <= 0

def registrar_evento(tipo, detalhe="", score=0, categoria="sistema"):
    historico.append({
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "usuario": st.session_state.email_usuario if st.session_state.logado else "anonimo",
        "tipo": tipo,
        "categoria": categoria,
        "score": score,
        "detalhe": detalhe
    })
    salvar_json(HIST_FILE, historico)

def adicionar_uso():
    if not st.session_state.logado:
        return
    if premium_ativo():
        return

    email = st.session_state.email_usuario
    usuarios[email]["uso"] = usuarios[email].get("uso", 0) + 1
    salvar_json(USERS_FILE, usuarios)

# =========================================================
# SIDEBAR - LOGIN
# =========================================================
st.sidebar.title("👤 Conta")

opcao = st.sidebar.selectbox(
    "Escolha uma opção",
    ["Entrar", "Criar conta", "Recuperar senha"]
)

if opcao == "Entrar":
    email_login = st.sidebar.text_input("Email", key="login_email")
    senha_login = st.sidebar.text_input("Senha", type="password", key="login_senha")

    if st.sidebar.button("Entrar"):
        if not email_login or not senha_login:
            st.sidebar.warning("Preencha todos os campos.")
        elif email_login in usuarios:
            senha_salva = usuarios[email_login].get("senha", "")
            if senha_salva == hash_senha(senha_login):
                st.session_state.logado = True
                st.session_state.email_usuario = email_login
                registrar_evento("login", "Login realizado")
                st.sidebar.success("Login realizado")
                st.rerun()
            else:
                st.sidebar.error("Senha incorreta")
        else:
            st.sidebar.error("Conta não encontrada")

elif opcao == "Criar conta":
    novo_email = st.sidebar.text_input("Novo email", key="novo_email")
    nova_senha = st.sidebar.text_input("Nova senha", type="password", key="nova_senha")

    if st.sidebar.button("Criar conta"):
        if not novo_email or not nova_senha:
            st.sidebar.warning("Preencha todos os campos.")
        elif novo_email.lower() == ADMIN_EMAIL.lower():
            st.sidebar.error("Email reservado.")
        elif novo_email in usuarios:
            st.sidebar.warning("Conta já existe.")
        else:
            usuarios[novo_email] = {
                "senha": hash_senha(nova_senha),
                "uso": 0,
                "premium": False,
                "premium_expira": ""
            }
            salvar_json(USERS_FILE, usuarios)

            st.session_state.logado = True
            st.session_state.email_usuario = novo_email
            registrar_evento("cadastro", "Conta criada")
            st.sidebar.success("Conta criada com sucesso")
            st.rerun()

elif opcao == "Recuperar senha":
    email_rec = st.sidebar.text_input("Email", key="rec_email")
    nova_senha = st.sidebar.text_input("Nova senha", type="password", key="rec_senha")

    if st.sidebar.button("Redefinir senha"):
        if not email_rec or not nova_senha:
            st.sidebar.warning("Preencha todos os campos.")
        elif email_rec in usuarios:
            usuarios[email_rec]["senha"] = hash_senha(nova_senha)
            salvar_json(USERS_FILE, usuarios)
            registrar_evento("senha", f"Senha redefinida para {email_rec}")
            st.sidebar.success("Senha atualizada")
        else:
            st.sidebar.error("Email não encontrado")

# =========================================================
# SIDEBAR - STATUS
# =========================================================
if st.session_state.logado:
    st.sidebar.success(f"👤 {st.session_state.email_usuario}")

    if premium_ativo():
        user = usuario_logado()
        exp = user.get("premium_expira", "")
        if exp:
            st.sidebar.success(f"💎 Premium ativo até {exp}")
        else:
            st.sidebar.success("💎 Premium ativo")
    else:
        st.sidebar.info(f"Análises grátis restantes: {uso_restante()}")

    if st.sidebar.button("Sair"):
        registrar_evento("logout", "Saiu da conta")
        st.session_state.logado = False
        st.session_state.email_usuario = ""
        st.rerun()
else:
    st.sidebar.info("Entre ou crie uma conta para usar o sistema.")

# =========================================================
# SIDEBAR - ADMIN
# =========================================================
if is_admin():
    st.sidebar.markdown("## 🔧 Admin")
    pagina_admin = st.sidebar.selectbox(
        "Painel Admin",
        ["Usuários", "Premium", "Resetar Senha", "Excluir Usuário", "Histórico Geral"]
    )

    if pagina_admin == "Usuários":
        st.markdown("<div class='admin'><h3>👥 Usuários cadastrados</h3></div>", unsafe_allow_html=True)

        if usuarios:
            lista = []
            for email, dados in usuarios.items():
                lista.append({
                    "Email": email,
                    "Uso": dados.get("uso", 0),
                    "Premium": dados.get("premium", False),
                    "Expira": dados.get("premium_expira", "-")
                })
            df = pd.DataFrame(lista)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nenhum usuário cadastrado.")

    elif pagina_admin == "Premium":
        st.markdown("<div class='admin'><h3>💎 Gerenciar Premium</h3></div>", unsafe_allow_html=True)

        email_sel = st.selectbox("Selecionar usuário", list(usuarios.keys()), key="admin_premium_user")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Ativar 30 dias"):
                usuarios[email_sel]["premium"] = True
                usuarios[email_sel]["premium_expira"] = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                salvar_json(USERS_FILE, usuarios)
                registrar_evento("admin", f"Premium 30 dias para {email_sel}")
                st.success("Premium ativado por 30 dias")

        with col2:
            if st.button("Ativar sem prazo"):
                usuarios[email_sel]["premium"] = True
                usuarios[email_sel]["premium_expira"] = ""
                salvar_json(USERS_FILE, usuarios)
                registrar_evento("admin", f"Premium sem prazo para {email_sel}")
                st.success("Premium ativado sem prazo")

        with col3:
            if st.button("Remover Premium"):
                usuarios[email_sel]["premium"] = False
                usuarios[email_sel]["premium_expira"] = ""
                salvar_json(USERS_FILE, usuarios)
                registrar_evento("admin", f"Premium removido de {email_sel}")
                st.warning("Premium removido")

    elif pagina_admin == "Resetar Senha":
        st.markdown("<div class='admin'><h3>🔑 Resetar senha</h3></div>", unsafe_allow_html=True)

        email_reset = st.selectbox("Usuário", list(usuarios.keys()), key="admin_reset_user")
        nova_senha_admin = st.text_input("Nova senha", type="password", key="admin_nova_senha")

        if st.button("Resetar senha"):
            if not nova_senha_admin:
                st.warning("Digite uma nova senha.")
            else:
                usuarios[email_reset]["senha"] = hash_senha(nova_senha_admin)
                salvar_json(USERS_FILE, usuarios)
                registrar_evento("admin", f"Senha resetada para {email_reset}")
                st.success("Senha atualizada")

    elif pagina_admin == "Excluir Usuário":
        st.markdown("<div class='admin'><h3>🗑️ Excluir usuário</h3></div>", unsafe_allow_html=True)

        email_del = st.selectbox("Usuário", list(usuarios.keys()), key="admin_delete_user")

        if st.button("Excluir usuário"):
            if email_del == ADMIN_EMAIL:
                st.error("Não pode excluir o admin.")
            else:
                usuarios.pop(email_del, None)
                salvar_json(USERS_FILE, usuarios)
                registrar_evento("admin", f"Usuário excluído: {email_del}")
                st.success("Usuário removido")

    elif pagina_admin == "Histórico Geral":
        st.markdown("<div class='admin'><h3>📊 Histórico geral</h3></div>", unsafe_allow_html=True)

        if historico:
            df_hist = pd.DataFrame(historico)
            st.dataframe(df_hist, use_container_width=True)
        else:
            st.info("Sem histórico.")

# =========================================================
# TELA PRINCIPAL
# =========================================================
st.title("🛡️ Escudo Digital IA")
st.subheader("Proteção inteligente contra golpes digitais")

st.markdown(f"""
<div class='premium'>
<b>Plano Premium</b><br>
Análises ilimitadas • mais controle • mais proteção<br><br>
<b>Preço:</b> {PRECO_PREMIUM}
</div>
""", unsafe_allow_html=True)

if not st.session_state.logado:
    st.warning("Faça login para usar o sistema.")
    st.markdown("<div class='bloco'><b>💳 Pagamento via Pix</b></div>", unsafe_allow_html=True)
    st.code(PIX_CODE)
    st.info("Após pagar, envie o comprovante para ativação do Premium.")
    st.stop()

# =========================================================
# STATUS USUÁRIO
# =========================================================
user = usuario_logado()

col1, col2, col3 = st.columns(3)
col1.metric("Usuário", st.session_state.email_usuario)
col2.metric("Premium", "Ativo" if premium_ativo() else "Free")
col3.metric("Restantes", "Ilimitado" if premium_ativo() else uso_restante())

# =========================================================
# BLOQUEIO FREE
# =========================================================
if limite_atingido():
    st.error("🚫 Você atingiu o limite gratuito.")
    st.markdown("<div class='premium'><b>Ative o Premium para continuar</b></div>", unsafe_allow_html=True)
    st.code(PIX_CODE)
    st.info("Após o pagamento, envie o comprovante para liberar o acesso.")
    st.stop()

# =========================================================
# ÁREA DE ANÁLISE
# =========================================================
st.markdown("<div class='bloco'><h3>🔎 Fazer análise</h3></div>", unsafe_allow_html=True)

tipo_analise = st.selectbox(
    "Tipo de análise",
    ["Mensagem suspeita", "Link suspeito", "Email suspeito", "Conversa de WhatsApp"]
)

entrada = st.text_area("Cole o conteúdo para análise")

def avaliar_texto(texto):
    texto_l = (texto or "").lower()
    score = 0
    sinais = []

    palavras_risco = [
        "pix", "urgente", "senha", "login", "código", "codigo",
        "clique aqui", "conta bloqueada", "empréstimo", "emprestimo",
        "facção", "faccao", "ameaça", "ameaca", "transferência",
        "transferencia", "troquei de número", "troquei de numero"
    ]

    for palavra in palavras_risco:
        if palavra in texto_l:
            score += 2
            sinais.append(palavra)

    if "http://" in texto_l or "https://" in texto_l:
        score += 1
        sinais.append("link detectado")

    if score >= 8:
        nivel = "🔴 Alto risco"
    elif score >= 4:
        nivel = "🟡 Suspeito"
    else:
        nivel = "🟢 Baixo risco"

    return score, nivel, sorted(set(sinais))

if st.button("Analisar agora"):
    if not entrada.strip():
        st.warning("Cole algum conteúdo para análise.")
    else:
        adicionar_uso()
        score, nivel, sinais = avaliar_texto(entrada)

        if score >= 8:
            st.error("Golpe altamente provável")
        elif score >= 4:
            st.warning("Conteúdo suspeito")
        else:
            st.success("Baixo risco")

        st.write("**Tipo:**", tipo_analise)
        st.write("**Score:**", score)
        st.write("**Nível:**", nivel)

        if sinais:
            st.write("**Sinais detectados:**", ", ".join(sinais))
        else:
            st.write("**Sinais detectados:** nenhum sinal forte")

        registrar_evento(
            tipo="analise",
            detalhe=f"{tipo_analise}: {entrada[:120]}",
            score=score,
            categoria=tipo_analise
        )

# =========================================================
# HISTÓRICO DO USUÁRIO
# =========================================================
st.markdown("<div class='bloco'><h3>📚 Meu histórico</h3></div>", unsafe_allow_html=True)

hist_user = [h for h in historico if h.get("usuario") == st.session_state.email_usuario]

if hist_user:
    df_user = pd.DataFrame(hist_user)
    st.dataframe(df_user, use_container_width=True)
else:
    st.info("Nenhum histórico ainda.")
