import streamlit as st
import requests
import pandas as pd
import json
import datetime
import io
import difflib
import re
from urllib.parse import urlparse
from PIL import Image
from reportlab.pdfgen import canvas

try:
    import pytesseract
    OCR_OK = True
except Exception:
    OCR_OK = False

try:
    import qrcode
    QR_OK = True
except Exception:
    QR_OK = False

try:
    import folium
    from streamlit_folium import st_folium
    MAP_OK = True
except Exception:
    MAP_OK = False


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(page_title="Escudo Digital IA", layout="wide")
st.set_option("client.showErrorDetails", False)

PIX_CODE = "00020126580014BR.GOV.BCB.PIX01365cecf979-d86a-4b71-9f03-a807d013e28a52040000530398654049.905802BR5915Ariel Jose Luiz6009SAO PAULO62140510tYrHuV1cyX63044599"
PRECO_PREMIUM = "R$ 9,90/mês"
LIMITE_GRATIS = 7

USERS_FILE = "usuarios.json"
HIST_FILE = "historico.json"
MAPA_FILE = "mapa_ips.json"
COMMUNITY_FILE = "comunidade.json"


# =========================================================
# TEMA
# =========================================================

st.markdown("""
<style>
.stApp{
    background: linear-gradient(135deg,#eef4ff,#d9e8ff);
    color:#0f172a;
}
h1,h2,h3{
    color:#1d4ed8;
}
p,span,label,div{
    color:#0f172a !important;
}
input, textarea{
    background:white !important;
    color:black !important;
    border-radius:10px !important;
}
.stButton>button{
    background:linear-gradient(90deg,#60a5fa,#2563eb);
    border-radius:12px;
    color:white;
    font-weight:bold;
    border:none;
}
.caixa-defesa{
    background:#eff6ff;
    border:1px solid #bfdbfe;
    border-radius:12px;
    padding:14px;
    margin-top:10px;
}
.caixa-idoso{
    background:#fff7ed;
    border:1px solid #fdba74;
    border-radius:12px;
    padding:14px;
    margin-top:10px;
}
.caixa-premium{
    background:#ecfeff;
    border:1px solid #67e8f9;
    border-radius:12px;
    padding:14px;
    margin-top:10px;
}
.caixa-info{
    background:#f8fafc;
    border:1px solid #cbd5e1;
    border-radius:12px;
    padding:14px;
    margin-top:10px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# JSON
# =========================================================

def carregar_json(nome_arquivo, padrao):
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return padrao

def salvar_json(nome_arquivo, dados):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

usuarios = carregar_json(USERS_FILE, {})
historico = carregar_json(HIST_FILE, [])
mapa_ips = carregar_json(MAPA_FILE, [])
comunidade = carregar_json(COMMUNITY_FILE, {})


# =========================================================
# SESSÃO
# =========================================================

if "logado" not in st.session_state:
    st.session_state.logado = False

if "email_usuario" not in st.session_state:
    st.session_state.email_usuario = ""

if "premium_demo" not in st.session_state:
    st.session_state.premium_demo = False


# =========================================================
# BASES
# =========================================================

sites_legitimos = [
    "google.com",
    "facebook.com",
    "instagram.com",
    "paypal.com",
    "amazon.com",
    "mercadolivre.com.br",
    "gov.br",
    "bb.com.br",
    "caixa.gov.br",
    "itau.com.br",
    "bradesco.com.br",
    "nubank.com.br",
    "santander.com.br"
]

bancos_legitimos = [
    "itau.com.br",
    "bb.com.br",
    "bradesco.com.br",
    "nubank.com.br",
    "caixa.gov.br",
    "santander.com.br"
]

indicadores = {
    "phishing_bancario": [
        "senha", "login", "banco", "verificação", "verificacao",
        "codigo", "código", "confirme", "conta bloqueada",
        "segurança", "seguranca", "acesso", "conta"
    ],
    "golpe_pix": [
        "pix", "chave pix", "transferência", "transferencia",
        "pix urgente", "manda pix", "pagamento imediato",
        "comprovante", "estorno"
    ],
    "emprestimo_falso": [
        "empréstimo", "emprestimo", "pré-aprovado", "pre-aprovado",
        "crédito", "credito", "taxa", "liberação", "liberacao",
        "valor aprovado", "oferta", "veículo em garantia",
        "veiculo em garantia", "parcelas", "consignado"
    ],
    "extorsao": [
        "facção", "faccao", "pcc", "cv", "comando",
        "estamos monitorando", "sua família", "sua familia",
        "se não pagar", "se nao pagar", "pague agora",
        "resolva isso agora", "ameaça", "ameaca"
    ],
    "engenharia_social": [
        "urgente", "agora", "hoje", "imediatamente",
        "clique aqui", "última chance", "ultima chance",
        "não perca", "nao perca"
    ],
    "golpe_idoso": [
        "aposentado", "aposentadoria", "benefício",
        "beneficio", "inss", "consignado"
    ],
    "whatsapp_golpe": [
        "whatsapp", "zap", "troquei de número", "troquei de numero",
        "grupo da família", "grupo da familia", "me chama aqui"
    ]
}

golpes_conhecidos = {
    "golpe_pix": "pedido urgente de transferência ou chave Pix",
    "emprestimo_falso": "promessa de crédito fácil, pré-aprovado ou taxa de liberação",
    "phishing_banco": "mensagem pedindo login, senha ou confirmação de conta",
    "extorsao": "mensagem com ameaça, facção ou pedido de dinheiro",
    "golpe_idoso": "mensagem envolvendo INSS, aposentadoria ou consignado",
    "golpe_whatsapp": "mensagem com urgência, troca de número ou pedido financeiro"
}


# =========================================================
# USUÁRIO
# =========================================================

def garantir_usuario(email):
    if email not in usuarios:
        usuarios[email] = {
            "senha": "",
            "uso": 0,
            "premium": False
        }
        salvar_json(USERS_FILE, usuarios)

def usuario_atual():
    if not st.session_state.logado:
        return None
    email = st.session_state.email_usuario
    garantir_usuario(email)
    return usuarios[email]

def premium_ativo():
    user = usuario_atual()
    if not user:
        return False
    return user.get("premium", False) or st.session_state.premium_demo

def uso_restante():
    user = usuario_atual()
    if not user:
        return LIMITE_GRATIS
    return max(0, LIMITE_GRATIS - user.get("uso", 0))

def limite_atingido():
    user = usuario_atual()
    if not user:
        return False
    if premium_ativo():
        return False
    return user.get("uso", 0) >= LIMITE_GRATIS

def contar_uso():
    user = usuario_atual()
    if user and not premium_ativo():
        user["uso"] = user.get("uso", 0) + 1
        usuarios[st.session_state.email_usuario] = user
        salvar_json(USERS_FILE, usuarios)


# =========================================================
# FUNÇÕES
# =========================================================

def registrar(tipo, score, detalhe="", categoria=""):
    historico.append({
        "data": str(datetime.datetime.now()),
        "usuario": st.session_state.email_usuario if st.session_state.logado else "anonimo",
        "tipo": tipo,
        "score": score,
        "categoria": categoria,
        "detalhe": detalhe
    })
    salvar_json(HIST_FILE, historico)

def registrar_ip(ip, lat, lon, pais, isp):
    registro = {
        "ip": ip,
        "lat": lat,
        "lon": lon,
        "pais": pais,
        "isp": isp
    }
    if registro not in mapa_ips:
        mapa_ips.append(registro)
        salvar_json(MAPA_FILE, mapa_ips)

def extrair_dominio(url_ou_dominio):
    txt = (url_ou_dominio or "").strip()
    if not txt:
        return ""
    if "://" not in txt:
        txt = "http://" + txt
    try:
        return urlparse(txt).netloc.lower().replace("www.", "")
    except Exception:
        return url_ou_dominio.lower().replace("www.", "").strip()

def score_para_risco(score):
    if score <= 3:
        return "🟢 Baixo"
    if score <= 6:
        return "🟡 Suspeito"
    if score <= 9:
        return "🟠 Provável golpe"
    return "🔴 Altíssimo"

def classificar_texto(texto):
    texto_l = (texto or "").lower()
    score = 0
    achados = []
    categorias = []

    for categoria, palavras in indicadores.items():
        hits = 0
        for p in palavras:
            if p in texto_l:
                hits += 1
                achados.append(p)

        if hits > 0:
            categorias.append(categoria)
            if categoria in [
                "emprestimo_falso",
                "phishing_bancario",
                "golpe_pix",
                "extorsao",
                "golpe_idoso",
                "whatsapp_golpe"
            ]:
                score += hits * 2
            else:
                score += hits

    for n in ["100.000", "200.000", "300.000", "500.000", "830.000", "100000", "200000", "300000", "500000", "830000"]:
        if n in texto_l:
            score += 2
            achados.append(f"valor alto {n}")

    categoria_final = "baixo_risco"

    if "extorsao" in categorias:
        categoria_final = "possivel_extorsao"
    elif "emprestimo_falso" in categorias:
        categoria_final = "possivel_emprestimo_falso"
    elif "golpe_pix" in categorias:
        categoria_final = "possivel_golpe_pix"
    elif "phishing_bancario" in categorias:
        categoria_final = "possivel_phishing_bancario"
    elif "golpe_idoso" in categorias:
        categoria_final = "possivel_golpe_financeiro"
    elif "whatsapp_golpe" in categorias:
        categoria_final = "possivel_golpe_whatsapp"
    elif "engenharia_social" in categorias:
        categoria_final = "engenharia_social"

    return score, categoria_final, sorted(set(achados))

def detectar_dominio_falso(url):
    dominio = extrair_dominio(url)
    risco = 0
    motivos = []

    for token in ["login", "secure", "verify", "update", "account", "confirm", "seguro", "seguranca"]:
        if token in dominio:
            risco += 1
            motivos.append(token)

    for site in sites_legitimos:
        similaridade = difflib.SequenceMatcher(None, dominio, site).ratio()
        if similaridade > 0.60 and dominio != site:
            risco += 2
            motivos.append(f"parecido com {site}")

    categoria = "dominio_suspeito" if risco > 0 else "baixo_risco"
    return dominio, risco, categoria, sorted(set(motivos))

def detectar_site_clone_banco(url):
    dominio = extrair_dominio(url)
    clones = []
    for banco in bancos_legitimos:
        similaridade = difflib.SequenceMatcher(None, dominio, banco).ratio()
        if similaridade > 0.65 and dominio != banco:
            clones.append((banco, similaridade))
    return clones

def reputacao_heuristica_dominio(url):
    dominio = extrair_dominio(url)
    risco = 0
    notas = []

    if len(dominio) > 28:
        risco += 2
        notas.append("domínio muito longo")

    if dominio.count("-") >= 2:
        risco += 2
        notas.append("muitos hífens")

    if re.search(r"\d", dominio):
        risco += 1
        notas.append("contém números")

    if any(x in dominio for x in ["login", "secure", "verify", "account", "update", "seguro"]):
        risco += 2
        notas.append("palavras típicas de phishing")

    if dominio.endswith(".xyz") or dominio.endswith(".top") or dominio.endswith(".click") or dominio.endswith(".shop"):
        risco += 2
        notas.append("TLD suspeito")

    return dominio, risco, notas

def registrar_denuncia_comunidade(categoria):
    if categoria not in comunidade:
        comunidade[categoria] = 0
    comunidade[categoria] += 1
    salvar_json(COMMUNITY_FILE, comunidade)

def exibir_defesa(categoria):
    base = [
        "Não clique em links da mensagem.",
        "Confirme no site ou aplicativo oficial.",
        "Não envie senha, código, documentos ou Pix por impulso.",
        "Peça ajuda a alguém de confiança antes de tomar decisão financeira."
    ]

    extras = {
        "possivel_emprestimo_falso": [
            "Bancos não cobram taxa antecipada para liberar empréstimo.",
            "Promessas de crédito fácil e valor alto são sinais de alerta."
        ],
        "possivel_golpe_pix": [
            "Golpistas usam urgência para forçar transferências rápidas."
        ],
        "possivel_extorsao": [
            "Golpistas usam ameaça para causar medo.",
            "Não faça pagamentos.",
            "Bloqueie o número e registre ocorrência."
        ],
        "possivel_phishing_bancario": [
            "Nunca digite sua senha após clicar em link enviado por mensagem."
        ],
        "dominio_suspeito": [
            "Digite o endereço do site manualmente no navegador."
        ],
        "possivel_golpe_financeiro": [
            "Golpes ligados a aposentadoria, INSS ou consignado exigem atenção redobrada."
        ],
        "possivel_golpe_whatsapp": [
            "Desconfie de pedidos financeiros por WhatsApp, principalmente com urgência.",
            "Confirme por ligação ou vídeo antes de transferir dinheiro."
        ]
    }

    dicas = base + extras.get(categoria, [])
    html = "<div class='caixa-defesa'><b>🛡 Defesa recomendada</b><ul>"
    for d in dicas:
        html += f"<li>{d}</li>"
    html += "</ul></div>"
    st.markdown(html, unsafe_allow_html=True)

def exibir_idoso(categoria, modo_idoso):
    if not modo_idoso or categoria == "baixo_risco":
        return
    st.markdown("""
    <div class='caixa-idoso'>
    <b>👵 Orientação simples</b><br><br>
    ⚠ Isso pode ser golpe.<br>
    ❌ Não mande dinheiro.<br>
    ❌ Não clique em links.<br>
    👨‍👩‍👧 Peça ajuda para um familiar ou pessoa de confiança.
    </div>
    """, unsafe_allow_html=True)

def mostrar_resultado(score, categoria, achados, modo_idoso):
    if score >= 10:
        st.error("🚨 Golpe altamente provável")
    elif score >= 6:
        st.error("🚨 Alto risco de golpe")
    elif score >= 3:
        st.warning("⚠️ Conteúdo suspeito")
    else:
        st.success("🟢 Baixo risco")

    st.write("**Score:**", score)
    st.write("**Nível de risco:**", score_para_risco(score))
    st.write("**Categoria:**", categoria)

    if achados:
        st.write("**Sinais:**", ", ".join(achados))

    exibir_defesa(categoria)
    exibir_idoso(categoria, modo_idoso)

def mostrar_bloco_premium():
    st.markdown(f"""
    <div class='caixa-premium'>
    <h3>💎 Escudo Digital Premium</h3>
    <b>Proteção completa contra golpes digitais</b><br><br>
    ✔ Análises ilimitadas<br>
    ✔ Detector avançado de phishing<br>
    ✔ Scanner de sites falsos<br>
    ✔ Radar global de ameaças<br>
    ✔ Histórico completo SOC<br>
    ✔ Relatórios profissionais<br><br>
    <b>Plano Premium</b><br>
    Apenas <b>{PRECO_PREMIUM}</b>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("💳 Pagar com Pix")
    if QR_OK:
        try:
            qr_img = qrcode.make(PIX_CODE)
            st.image(qr_img, width=260)
        except Exception:
            pass
    st.write("Pix copia e cola:")
    st.code(PIX_CODE)
    st.info("Após o pagamento, clique em 'Ativar Premium (demo)' na barra lateral.")


# =========================================================
# LOGIN
# =========================================================

st.sidebar.title("👤 Conta")

opcao = st.sidebar.selectbox(
    "Escolha uma opção",
    ["Entrar", "Criar conta", "Recuperar senha"]
)

if opcao == "Entrar":
    email_login = st.sidebar.text_input("Email")
    senha_login = st.sidebar.text_input("Senha", type="password")

    if st.sidebar.button("Entrar"):
        if email_login in usuarios and usuarios[email_login]["senha"] == senha_login:
            st.session_state.logado = True
            st.session_state.email_usuario = email_login
            st.sidebar.success("✅ Login realizado")
            st.rerun()
        else:
            st.sidebar.error("Email ou senha inválidos")

elif opcao == "Criar conta":
    novo_email = st.sidebar.text_input("Novo email")
    nova_senha = st.sidebar.text_input("Nova senha", type="password")

    if st.sidebar.button("Criar conta"):
        if not novo_email or not nova_senha:
            st.sidebar.warning("Preencha email e senha")
        elif novo_email in usuarios:
            st.sidebar.warning("Conta já existe")
        else:
            usuarios[novo_email] = {
                "senha": nova_senha,
                "uso": 0,
                "premium": False
            }
            salvar_json(USERS_FILE, usuarios)
            st.session_state.logado = True
            st.session_state.email_usuario = novo_email
            st.sidebar.success("✅ Conta criada")
            st.rerun()

elif opcao == "Recuperar senha":
    email_rec = st.sidebar.text_input("Digite seu email")

    if st.sidebar.button("Recuperar senha"):
        if email_rec in usuarios:
            st.sidebar.success("Sua senha é:")
            st.sidebar.code(usuarios[email_rec]["senha"])
        else:
            st.sidebar.error("Email não encontrado")

if st.session_state.logado:
    st.sidebar.success(f"👤 {st.session_state.email_usuario}")

    if premium_ativo():
        st.sidebar.success("💎 Premium ativo")
    else:
        st.sidebar.info(f"Análises grátis restantes: {uso_restante()}")

    if st.sidebar.button("Ativar Premium (demo)"):
        st.session_state.premium_demo = True
        st.sidebar.success("💎 Premium ativado")
        st.rerun()

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.session_state.email_usuario = ""
        st.session_state.premium_demo = False
        st.rerun()
else:
    st.sidebar.info("Entre ou crie uma conta para usar o sistema.")


# =========================================================
# APP
# =========================================================

st.title("🛡️ ESCUDO DIGITAL IA")
st.subheader("SOC de monitoramento de golpes e análise OSINT")

st.markdown(f"""
<div class='caixa-premium'>
<b>💎 Modelo do app</b><br>
{LIMITE_GRATIS} análises grátis • depois premium sugerido: <b>{PRECO_PREMIUM}</b>
</div>
""", unsafe_allow_html=True)

modo_idoso = st.toggle("👵 Modo proteção para idosos", value=True)

if not st.session_state.logado:
    st.warning("Faça login ou crie uma conta na barra lateral para liberar as análises.")
    mostrar_bloco_premium()

bloqueado = (not st.session_state.logado) or limite_atingido()

if st.session_state.logado and limite_atingido():
    st.error("🚫 Você atingiu o limite de análises gratuitas.")
    mostrar_bloco_premium()


# =========================================================
# OSINT IP
# =========================================================

st.header("🌍 Análise OSINT de IP")
ip = st.text_input("Digite domínio ou IP")

if st.button("Analisar IP"):
    if bloqueado:
        st.warning("Faça login ou ative o Premium para continuar.")
        if limite_atingido():
            mostrar_bloco_premium()
    else:
        contar_uso()
        try:
            r = requests.get(f"http://ip-api.com/json/{ip}", timeout=10).json()
            if r.get("status") == "success":
                pais = r.get("country")
                cidade = r.get("city")
                isp = r.get("isp")
                asn = r.get("as")
                lat = r.get("lat")
                lon = r.get("lon")

                st.success("Consulta realizada")

                c1, c2 = st.columns(2)
                with c1:
                    st.write("**IP:**", ip)
                    st.write("**País:**", pais)
                    st.write("**Cidade:**", cidade)
                with c2:
                    st.write("**ISP:**", isp)
                    st.write("**ASN:**", asn)
                    st.write("**Organização:**", r.get("org"))

                registrar("ip", 1, ip, "osint_ip")

                if lat and lon:
                    registrar_ip(ip, lat, lon, pais, isp)

                    if MAP_OK:
                        mapa = folium.Map(location=[lat, lon], zoom_start=4)
                        folium.Marker(
                            [lat, lon],
                            popup=f"IP: {ip}<br>País: {pais}<br>ISP: {isp}",
                            tooltip="Clique para detalhes"
                        ).add_to(mapa)
                        st_folium(mapa, width=700, height=420)
            else:
                st.error("Não foi possível localizar o IP")
        except Exception:
            st.error("Erro ao consultar IP.")


# =========================================================
# RADAR GLOBAL
# =========================================================

st.header("🌎 Radar global de ameaças")

if MAP_OK:
    try:
        if mapa_ips:
            mapa = folium.Map(location=[0, 0], zoom_start=2)
            for item in mapa_ips:
                lat = item.get("lat")
                lon = item.get("lon")
                if lat and lon:
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=6,
                        color="red",
                        fill=True,
                        popup=f"IP: {item.get('ip','?')}<br>País: {item.get('pais','?')}<br>ISP: {item.get('isp','?')}"
                    ).add_to(mapa)
            st_folium(mapa, width=900, height=480)
        else:
            st.info("Nenhum IP analisado ainda.")
    except Exception:
        st.warning("Erro ao carregar o mapa global.")
else:
    st.info("Mapa indisponível neste ambiente.")


# =========================================================
# PHISHING
# =========================================================

st.header("🚨 Detector de Phishing")
msg = st.text_area("Cole mensagem suspeita")

if st.button("Analisar mensagem"):
    if bloqueado:
        st.warning("Faça login ou ative o Premium para continuar.")
        if limite_atingido():
            mostrar_bloco_premium()
    else:
        contar_uso()
        score, cat, achados = classificar_texto(msg)
        mostrar_resultado(score, cat, achados, modo_idoso)
        registrar("mensagem", score, msg[:150], cat)


# =========================================================
# WHATSAPP
# =========================================================

st.header("📱 Detector de golpes de WhatsApp")
zap = st.text_area("Cole a conversa suspeita do WhatsApp")

if st.button("Analisar conversa"):
    if bloqueado:
        st.warning("Faça login ou ative o Premium para continuar.")
        if limite_atingido():
            mostrar_bloco_premium()
    else:
        contar_uso()
        score, cat, achados = classificar_texto(zap)

        if "whatsapp" in zap.lower() or "troquei de número" in zap.lower() or "troquei de numero" in zap.lower():
            score += 2
            achados.append("padrão de golpe por WhatsApp")
            if cat == "baixo_risco":
                cat = "possivel_golpe_whatsapp"

        mostrar_resultado(score, cat, sorted(set(achados)), modo_idoso)
        registrar("whatsapp", score, zap[:150], cat)


# =========================================================
# DOMÍNIO
# =========================================================

st.header("🔎 Scanner de domínio")
dom = st.text_input("Digite URL suspeita")

if st.button("Analisar domínio"):
    if bloqueado:
        st.warning("Faça login ou ative o Premium para continuar.")
        if limite_atingido():
            mostrar_bloco_premium()
    else:
        contar_uso()
        dominio_extraido, score, categoria_dom, motivos = detectar_dominio_falso(dom)
        clones = detectar_site_clone_banco(dom)
        _, risco_rep, notas_rep = reputacao_heuristica_dominio(dom)

        if clones:
            st.error("🚨 Possível site clone de banco detectado")
            for banco, sim in clones:
                st.write(f"Parecido com: {banco} ({round(sim * 100, 1)}%)")
            score += 3

        st.write("**Domínio:**", dominio_extraido)
        st.write("**Score:**", score)
        st.write("**Nível de risco:**", score_para_risco(score))

        if motivos:
            st.write("**Motivos:**", ", ".join(motivos))

        st.markdown("<div class='caixa-info'><b>🔍 Reputação heurística do domínio</b></div>", unsafe_allow_html=True)
        st.write("**Risco heurístico:**", risco_rep)
        if notas_rep:
            st.write("**Notas:**", ", ".join(notas_rep))
        else:
            st.write("**Notas:** nenhum sinal forte")

        if score >= 3:
            st.warning("⚠️ Domínio suspeito")
        else:
            st.success("🟢 Domínio aparentemente seguro")

        exibir_defesa("dominio_suspeito" if score > 0 else "baixo_risco")
        exibir_idoso("dominio_suspeito" if score > 0 else "baixo_risco", modo_idoso)
        registrar("dominio", score, dominio_extraido, "dominio_suspeito" if score > 0 else "baixo_risco")


# =========================================================
# OCR
# =========================================================

st.header("📷 Analisar print de golpe")
arq = st.file_uploader("Envie print", type=["png", "jpg", "jpeg"])

if arq:
    if bloqueado:
        st.warning("Faça login ou ative o Premium para continuar.")
        if limite_atingido():
            mostrar_bloco_premium()
    else:
        contar_uso()
        img = Image.open(arq)
        st.image(img)

        if OCR_OK:
            try:
                texto = pytesseract.image_to_string(img)
                st.write("Texto detectado:")
                st.write(texto)

                score, cat, achados = classificar_texto(texto)
                mostrar_resultado(score, cat, achados, modo_idoso)
                registrar("imagem", score, texto[:150], cat)
            except Exception:
                st.warning("Erro ao ler a imagem.")
        else:
            st.warning("OCR não disponível no servidor.")


# =========================================================
# EMAIL
# =========================================================

st.header("📧 Analisar email suspeito")
email = st.text_area("Cole o email")

if st.button("Analisar email"):
    if bloqueado:
        st.warning("Faça login ou ative o Premium para continuar.")
        if limite_atingido():
            mostrar_bloco_premium()
    else:
        contar_uso()
        score, cat, achados = classificar_texto(email)
        mostrar_resultado(score, cat, achados, modo_idoso)
        registrar("email", score, email[:150], cat)


# =========================================================
# COMUNIDADE
# =========================================================

st.header("👥 Denúncia da comunidade")
categoria_denuncia = st.selectbox(
    "Categoria para denunciar",
    [
        "possivel_phishing_bancario",
        "possivel_golpe_pix",
        "possivel_emprestimo_falso",
        "possivel_extorsao",
        "possivel_golpe_financeiro",
        "possivel_golpe_whatsapp"
    ]
)

if st.button("🚨 Denunciar golpe"):
    registrar_denuncia_comunidade(categoria_denuncia)
    st.success("Denúncia registrada.")

if comunidade:
    df_com = pd.DataFrame([{"Categoria": k, "Denúncias": v} for k, v in comunidade.items()])
    df_com = df_com.sort_values("Denúncias", ascending=False)
    st.dataframe(df_com, use_container_width=True)


# =========================================================
# HISTÓRICO
# =========================================================

st.header("📊 Histórico SOC")

if historico:
    df = pd.DataFrame(historico)
    if st.session_state.logado and "usuario" in df.columns:
        df = df[df["usuario"] == st.session_state.email_usuario]
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nenhum evento registrado ainda.")


# =========================================================
# PAINEL
# =========================================================

st.header("📡 Painel SOC")

df_user = pd.DataFrame(historico) if historico else pd.DataFrame(columns=["score", "usuario", "data", "categoria"])
if not df_user.empty and st.session_state.logado and "usuario" in df_user.columns:
    df_user = df_user[df_user["usuario"] == st.session_state.email_usuario]

total = len(df_user)
sus = len(df_user[df_user["score"] >= 3]) if not df_user.empty else 0
alert = len(df_user[df_user["score"] >= 6]) if not df_user.empty else 0

c1, c2, c3 = st.columns(3)
c1.metric("Eventos detectados", total)
c2.metric("Eventos suspeitos", sus)
c3.metric("Alertas ativos", alert)


# =========================================================
# RADAR DE AMEAÇA
# =========================================================

st.header("🛰 Radar de ameaça")

if alert >= 4:
    st.error("🚨 Nível alto de ameaça")
elif alert >= 1:
    st.warning("⚠ Atividade suspeita")
else:
    st.success("🟢 Ambiente seguro")


# =========================================================
# RANKING
# =========================================================

st.header("📈 Ranking de golpes")

if not df_user.empty and "categoria" in df_user.columns:
    ranking = df_user["categoria"].value_counts().reset_index()
    ranking.columns = ["Categoria", "Quantidade"]
    st.dataframe(ranking, use_container_width=True)
else:
    st.info("Sem dados para ranking ainda.")


# =========================================================
# CAMPANHAS
# =========================================================

st.header("🚨 Campanhas de golpe")

if not df_user.empty and "categoria" in df_user.columns:
    repetidos = df_user["categoria"].value_counts()
    encontrou = False

    for tipo, valor in repetidos.items():
        if valor >= 3 and tipo != "baixo_risco":
            encontrou = True
            st.warning(f"Possível campanha ativa: {tipo} ({valor} ocorrências)")

    try:
        df_user = df_user.copy()
        df_user["data_dt"] = pd.to_datetime(df_user["data"])
        ultimas_24h = df_user[df_user["data_dt"] >= (pd.Timestamp.now() - pd.Timedelta(hours=24))]
        if not ultimas_24h.empty:
            top24 = ultimas_24h["categoria"].value_counts()
            for tipo, valor in top24.items():
                if valor >= 2 and tipo != "baixo_risco":
                    st.info(f"Últimas 24h: {tipo} ({valor} ocorrências)")
    except Exception:
        pass

    if not encontrou:
        st.success("Nenhuma campanha forte detectada no momento.")
else:
    st.info("Sem histórico suficiente para campanhas.")


# =========================================================
# BIBLIOTECA
# =========================================================

st.header("📚 Biblioteca de golpes")

for nome, desc in golpes_conhecidos.items():
    st.write(f"**{nome}** — {desc}")


# =========================================================
# CHAT
# =========================================================

st.header("🤖 Chat do Escudo")
chat = st.text_input("Pergunte algo")

def responder_chat(texto):
    score, cat, achados = classificar_texto(texto)

    if "ip" in texto.lower():
        partes = texto.split()
        for p in partes:
            if "." in p:
                try:
                    r = requests.get(f"http://ip-api.com/json/{p}", timeout=10).json()
                    if r.get("status") == "success":
                        return f"""🌍 IP analisado

IP: {p}
País: {r.get('country')}
Cidade: {r.get('city')}
ISP: {r.get('isp')}
ASN: {r.get('as')}"""
                except Exception:
                    pass

    if "site" in texto.lower() or "dominio" in texto.lower() or "link" in texto.lower():
        partes = texto.split()
        for p in partes:
            if "." in p:
                dominio, score_dom, cat_dom, motivos = detectar_dominio_falso(p)
                clones = detectar_site_clone_banco(p)

                resposta = f"""🔎 Análise de domínio

Domínio: {dominio}
Score: {score_dom}
Categoria: {cat_dom}
Risco: {score_para_risco(score_dom)}"""

                if motivos:
                    resposta += f"\nMotivos: {', '.join(motivos)}"

                if clones:
                    resposta += "\n🚨 Possível site clone de banco"

                return resposta

    if score > 0:
        return f"""🚨 Análise do chat

Score: {score}
Categoria: {cat}
Risco: {score_para_risco(score)}
Sinais: {", ".join(achados)}"""

    return """🤖 Posso ajudar com:

• analisar IP
• verificar site
• detectar golpes
• analisar conversa de WhatsApp

Exemplos:
analise ip 8.8.8.8
verificar site itau-login-seguro.com
isso é golpe de pix urgente
"""

if chat:
    if bloqueado:
        st.warning("Faça login ou ative o Premium para continuar usando o chat.")
        if limite_atingido():
            mostrar_bloco_premium()
    else:
        contar_uso()
        st.write(responder_chat(chat))
        score_chat, cat_chat, _ = classificar_texto(chat)
        registrar("chat", score_chat, chat[:150], cat_chat)


# =========================================================
# PDF
# =========================================================

st.header("📄 Gerar relatório")

if st.button("Gerar PDF"):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    y = 800
    c.drawString(40, y, "Relatório Escudo Digital IA")
    y -= 30

    df_pdf = pd.DataFrame(historico) if historico else pd.DataFrame()
    if not df_pdf.empty and st.session_state.logado and "usuario" in df_pdf.columns:
        df_pdf = df_pdf[df_pdf["usuario"] == st.session_state.email_usuario]

    for _, e in df_pdf.iterrows():
        linha = f"{e.get('data','')} | {e.get('tipo','')} | {e.get('categoria','')} | score:{e.get('score','')}"
        c.drawString(40, y, linha[:100])
        y -= 18
        if y < 60:
            c.showPage()
            y = 800

    c.save()

    st.download_button(
        "Baixar relatório",
        buffer.getvalue(),
        "relatorio_soc.pdf"
    )
