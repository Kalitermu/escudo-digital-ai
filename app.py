import streamlit as st
import json
import datetime

st.set_page_config(page_title="Escudo Digital IA", layout="wide")

USERS_FILE = "usuarios.json"
HIST_FILE = "historico.json"

PIX_CODE = "00020126580014BR.GOV.BCB.PIX01365cecf979-d86a-4b71-9f03-a807d013e28a52040000530398654049.905802BR5915Ariel Jose Luiz6009SAO PAULO62140510tYrHuV1cyX63044599"

LIMITE_GRATIS = 7


# ===============================
# ARQUIVOS
# ===============================

def carregar_json(arq):
    try:
        with open(arq, "r") as f:
            return json.load(f)
    except:
        return {}

def salvar_json(arq, dados):
    with open(arq, "w") as f:
        json.dump(dados, f, indent=2)


usuarios = carregar_json(USERS_FILE)
historico = carregar_json(HIST_FILE)


# ===============================
# SESSÃO
# ===============================

if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = None


# ===============================
# LOGIN
# ===============================

def tela_login():

    st.title("🔐 Login Escudo Digital")

    aba1, aba2 = st.tabs(["Entrar", "Criar Conta"])

    with aba1:

        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):

            if email in usuarios and usuarios[email]["senha"] == senha:

                st.session_state.logado = True
                st.session_state.usuario = email
                st.success("Login realizado")
                st.rerun()

            else:
                st.error("Email ou senha inválidos")

    with aba2:

        email = st.text_input("Novo Email")
        senha = st.text_input("Nova Senha", type="password")

        if st.button("Criar Conta"):

            if email in usuarios:
                st.warning("Conta já existe")
            else:

                usuarios[email] = {
                    "senha": senha,
                    "uso": 0,
                    "premium": False
                }

                salvar_json(USERS_FILE, usuarios)

                st.success("Conta criada")


# ===============================
# ANALISADOR SIMPLES
# ===============================

def analisar_texto(txt):

    txt = txt.lower()

    score = 0
    sinais = []

    palavras = [
        "pix",
        "emprestimo",
        "pré-aprovado",
        "urgente",
        "taxa",
        "liberação",
        "codigo",
        "senha",
        "pague agora"
    ]

    for p in palavras:

        if p in txt:
            score += 2
            sinais.append(p)

    categoria = "baixo_risco"

    if "emprestimo" in txt:
        categoria = "emprestimo_falso"

    if "pix" in txt:
        categoria = "golpe_pix"

    return score, categoria, sinais


# ===============================
# APP PRINCIPAL
# ===============================

def app():

    user = usuarios[st.session_state.usuario]

    st.sidebar.title("👤 Conta")

    st.sidebar.write(st.session_state.usuario)

    if user["premium"]:
        st.sidebar.success("💎 Premium ativo")
    else:
        restante = LIMITE_GRATIS - user["uso"]
        st.sidebar.info(f"Análises restantes: {restante}")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    if st.sidebar.button("Ativar Premium"):
        usuarios[st.session_state.usuario]["premium"] = True
        salvar_json(USERS_FILE, usuarios)
        st.sidebar.success("Premium ativado")

    st.title("🛡️ ESCUDO DIGITAL IA")
    st.subheader("SOC de monitoramento de golpes")

    if not user["premium"] and user["uso"] >= LIMITE_GRATIS:

        st.error("🚫 Limite grátis atingido")

        st.subheader("💎 Premium")

        st.write("Plano: R$ 9,90 / mês")

        st.write("Pix copia e cola")

        st.code(PIX_CODE)

        return

    # ==========================
    # ANALISADOR
    # ==========================

    st.header("🚨 Detector de Golpes")

    msg = st.text_area("Cole mensagem suspeita")

    if st.button("Analisar"):

        score, categoria, sinais = analisar_texto(msg)

        usuarios[st.session_state.usuario]["uso"] += 1
        salvar_json(USERS_FILE, usuarios)

        if score >= 6:
            st.error("🚨 Golpe provável")

        elif score >= 2:
            st.warning("⚠ Conteúdo suspeito")

        else:
            st.success("🟢 Baixo risco")

        st.write("Score:", score)
        st.write("Categoria:", categoria)

        if sinais:
            st.write("Sinais:", ", ".join(sinais))

        historico[str(datetime.datetime.now())] = {
            "user": st.session_state.usuario,
            "score": score,
            "categoria": categoria
        }

        salvar_json(HIST_FILE, historico)

    # ==========================
    # HISTÓRICO
    # ==========================

    st.header("📊 Histórico")

    for k, v in historico.items():

        if v["user"] == st.session_state.usuario:

            st.write(
                k,
                "-",
                v["categoria"],
                "- score:",
                v["score"]
            )


# ===============================
# EXECUÇÃO
# ===============================

if not st.session_state.logado:
    tela_login()
else:
    app()
