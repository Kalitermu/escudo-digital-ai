import streamlit as st
import requests
import pandas as pd
import json
import datetime
import io
import difflib
from PIL import Image
from reportlab.pdfgen import canvas
import folium
from streamlit_folium import st_folium

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


# =========================================
# CONFIG
# =========================================

st.set_page_config(page_title="Escudo Digital IA", layout="wide")

PIX_CODE = "00020126580014BR.GOV.BCB.PIX01365cecf979-d86a-4b71-9f03-a807d013e28a52040000530398654049.905802BR5915Ariel Jose Luiz6009SAO PAULO62140510tYrHuV1cyX63044599"
PRECO_PREMIUM = "R$ 9,90/mês"
LIMITE_GRATIS = 7

# =========================================
# TEMA VISUAL
# =========================================

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
[data-testid="stMetricValue"]{
    color:#0f172a !important;
    font-size:30px;
}
[data-testid="stMetricLabel"]{
    color:#1e40af !important;
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
.caixa-alerta{
    background:#fef2f2;
    border:1px solid #fecaca;
    border-radius:12px;
    padding:14px;
    margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

# =========================================
# ARQUIVOS
# =========================================

HIST_ARQ = "historico.json"
MAPA_ARQ = "mapa_ips.json"

def carregar_json(nome_arquivo):
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def salvar_json(nome_arquivo, dados):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

historico = carregar_json(HIST_ARQ)
mapa_ips = carregar_json(MAPA_ARQ)

# =========================================
# SESSÃO / LOGIN / PREMIUM
# =========================================

if "uso" not in st.session_state:
    st.session_state.uso = 0

if "premium" not in st.session_state:
    st.session_state.premium = False

if "logado" not in st.session_state:
    st.session_state.logado = False

if "email_usuario" not in st.session_state:
    st.session_state.email_usuario = ""

st.sidebar.title("👤 Conta")

email_login = st.sidebar.text_input("Email")
senha_login = st.sidebar.text_input("Senha", type="password")

col_login_1, col_login_2 = st.sidebar.columns(2)

with col_login_1:
    if st.button("Entrar"):
        if email_login and senha_login:
            st.session_state.logado = True
            st.session_state.email_usuario = email_login
            st.sidebar.success("✅ Login realizado")
        else:
            st.sidebar.warning("Preencha email e senha")

with col_login_2:
    if st.button("Criar conta"):
        if email_login and senha_login:
            st.session_state.logado = True
            st.session_state.email_usuario = email_login
            st.sidebar.success("✅ Conta criada")
        else:
            st.sidebar.warning("Preencha email e senha")

if st.session_state.logado:
    st.sidebar.success(f"👤 {st.session_state.email_usuario}")
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.session_state.email_usuario = ""
        st.rerun()

if st.sidebar.button("Ativar Premium (demo)"):
    st.session_state.premium = True
    st.sidebar.success("💎 Premium ativado")

if st.session_state.premium:
    st.sidebar.success("💎 Premium ativo")
else:
    restante = max(0, LIMITE_GRATIS - st.session_state.uso)
    st.sidebar.info(f"Análises grátis restantes: {restante}")

limite_atingido = (not st.session_state.premium) and (st.session_state.uso >= LIMITE_GRATIS)

def contar_uso():
    if not st.session_state.premium and not limite_atingido:
        st.session_state.uso += 1

# =========================================
# DADOS DE REGRAS
# =========================================

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
    ]
}

golpes_conhecidos = {
    "golpe_pix": "pedido urgente de transferência ou chave Pix",
    "emprestimo_falso": "promessa de crédito fácil, pré-aprovado ou taxa de liberação",
    "phishing_banco": "mensagem pedindo login, senha ou confirmação de conta",
    "extorsao": "mensagem com ameaça, facção ou pedido de dinheiro",
    "golpe_idoso": "mensagem envolvendo INSS, aposentadoria ou consignado"
}

# =========================================
# FUNÇÕES
# =========================================

def registrar(tipo, score, detalhe="", categoria="", defesa=""):
    evento = {
        "data": str(datetime.datetime.now()),
        "tipo": tipo,
        "score": score,
        "categoria": categoria,
        "detalhe": detalhe,
        "defesa": defesa
    }
    historico.append(evento)
    salvar_json(HIST_ARQ, historico)

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
        salvar_json(MAPA_ARQ, mapa_ips)

def classificar_texto(texto):
    texto_l = texto.lower()
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
            if categoria in ["emprestimo_falso", "phishing_bancario", "golpe_pix", "extorsao", "golpe_idoso"]:
                score += hits * 2
            else:
                score += hits

    numeros_altos = [
        "100.000", "200.000", "300.000", "500.000", "830.000",
        "100000", "200000", "300000", "500000", "830000"
    ]

    for n in numeros_altos:
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
    elif "engenharia_social" in categorias:
        categoria_final = "engenharia_social"

    return score, categoria_final, sorted(set(achados))

def detectar_dominio_falso(url):
    url = url.lower().strip().replace("https://", "").replace("http://", "").strip("/")
    risco = 0
    motivos = []

    tokens_suspeitos = [
        "login", "secure", "verify", "update", "account",
        "confirm", "seguro", "seguranca"
    ]

    for token in tokens_suspeitos:
        if token in url:
            risco += 1
            motivos.append(token)

    for site in sites_legitimos:
        similaridade = difflib.SequenceMatcher(None, url, site).ratio()
        if similaridade > 0.60 and url != site:
            risco += 2
            motivos.append(f"parecido com {site}")

    categoria = "dominio_suspeito" if risco > 0 else "baixo_risco"
    return risco, categoria, sorted(set(motivos))

def detectar_site_clone_banco(url):
    url = url.lower().strip().replace("https://", "").replace("http://", "").strip("/")
    clones = []

    for banco in bancos_legitimos:
        similaridade = difflib.SequenceMatcher(None, url, banco).ratio()
        if similaridade > 0.65 and url != banco:
            clones.append((banco, similaridade))

    return clones

def defesa_recomendada(categoria):
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
        ]
    }

    return base + extras.get(categoria, [])

def exibir_defesa(categoria):
    dicas = defesa_recomendada(categoria)
    html = "<div class='caixa-defesa'><b>🛡 Defesa recomendada</b><ul>"
    for d in dicas:
        html += f"<li>{d}</li>"
    html += "</ul></div>"
    st.markdown(html, unsafe_allow_html=True)

def exibir_modo_idoso(categoria):
    if not modo_idoso or categoria == "baixo_risco":
        return

    html = """
    <div class='caixa-idoso'>
    <b>👵 Orientação simples</b><br><br>
    ⚠ Isso pode ser golpe.<br>
    ❌ Não mande dinheiro.<br>
    ❌ Não clique em links.<br>
    👨‍👩‍👧 Peça ajuda para um familiar ou pessoa de confiança.
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def mostrar_resultado(score, categoria, achados):
    if score >= 10:
        st.error("🚨 Golpe altamente provável")
    elif score >= 6:
        st.error("🚨 Alto risco de golpe")
    elif score >= 3:
        st.warning("⚠️ Conteúdo suspeito")
    else:
        st.success("🟢 Baixo risco")

    st.write("**Score:**", score)
    st.write("**Categoria:**", categoria)

    if achados:
        st.write("**Sinais:**", ", ".join(achados))

    exibir_defesa(categoria)
    exibir_modo_idoso(categoria)

def mostrar_bloco_premium():
    st.markdown(f"""
<div class='caixa-premium'>
<b>💎 Escudo Digital Premium</b><br><br>
Você usou as {LIMITE_GRATIS} análises grátis.<br>
Para continuar:<br>
• Crie conta<br>
• Ative premium<br><br>
<b>{PRECO_PREMIUM}</b>
</div>
""", unsafe_allow_html=True)

    st.subheader("💳 Pagar com Pix")
    st.write(f"Plano Premium: **{PRECO_PREMIUM}**")

    if QR_OK:
        qr_img = qrcode.make(PIX_CODE)
        st.image(qr_img, width=260)

    st.write("Pix copia e cola:")
    st.code(PIX_CODE)

    st.info("Após o pagamento, libere o premium manualmente no botão da barra lateral.")

# =========================================
# CABEÇALHO
# =========================================

st.title("🛡️ ESCUDO DIGITAL IA")
st.subheader("SOC de monitoramento de golpes e análise OSINT")

st.markdown(f"""
<div class='caixa-premium'>
<b>💎 Modelo do app</b><br>
{LIMITE_GRATIS} análises grátis • depois premium sugerido: <b>{PRECO_PREMIUM}</b>
</div>
""", unsafe_allow_html=True)

modo_idoso = st.toggle("👵 Modo proteção para idosos", value=True)

if limite_atingido:
    st.error("🚫 Você atingiu o limite de análises gratuitas.")
    mostrar_bloco_premium()

# =========================================
# OSINT IP
# =========================================

st.header("🌍 Análise OSINT de IP")

ip = st.text_input("Digite domínio ou IP")

if st.button("Analisar IP") and not limite_atingido:
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
        st.error("Erro na consulta")

# =========================================
# RADAR GLOBAL
# =========================================

st.header("🌎 Radar global de ameaças")

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

# =========================================
# PHISHING
# =========================================

st.header("🚨 Detector de Phishing")

msg = st.text_area("Cole mensagem suspeita")

if st.button("Analisar mensagem") and not limite_atingido:
    contar_uso()
    score, cat, achados = classificar_texto(msg)
    mostrar_resultado(score, cat, achados)
    registrar("mensagem", score, msg[:150], cat)

# =========================================
# DOMÍNIO
# =========================================

st.header("🔎 Scanner de domínio")

dom = st.text_input("Digite URL suspeita")

if st.button("Analisar domínio") and not limite_atingido:
    contar_uso()
    score, categoria_dom, motivos = detectar_dominio_falso(dom)

    clones = detectar_site_clone_banco(dom)
    if clones:
        st.error("🚨 Possível site clone de banco detectado")
        for banco, sim in clones:
            st.write(f"Parecido com: {banco} ({round(sim * 100, 1)}%)")
        score += 3

    if score >= 3:
        st.warning("⚠️ Domínio suspeito")
    else:
        st.success("🟢 Domínio aparentemente seguro")

    st.write("**Score:**", score)

    if motivos:
        st.write("**Motivos:**", ", ".join(motivos))

    exibir_defesa("dominio_suspeito" if score > 0 else "baixo_risco")
    exibir_modo_idoso("dominio_suspeito" if score > 0 else "baixo_risco")

    registrar("dominio", score, dom, "dominio_suspeito" if score > 0 else "baixo_risco")

# =========================================
# OCR
# =========================================

st.header("📷 Analisar print de golpe")

arq = st.file_uploader("Envie print", type=["png", "jpg", "jpeg"])

if arq and not limite_atingido:
    contar_uso()
    img = Image.open(arq)
    st.image(img)

    if OCR_OK:
        try:
            texto = pytesseract.image_to_string(img)

            st.write("Texto detectado:")
            st.write(texto)

            score, cat, achados = classificar_texto(texto)
            mostrar_resultado(score, cat, achados)

            registrar("imagem", score, texto[:150], cat)
        except Exception:
            st.warning("OCR não disponível")
    else:
        st.warning("OCR não disponível no servidor")

# =========================================
# EMAIL
# =========================================

st.header("📧 Analisar email suspeito")

email = st.text_area("Cole o email")

if st.button("Analisar email") and not limite_atingido:
    contar_uso()
    score, cat, achados = classificar_texto(email)
    mostrar_resultado(score, cat, achados)
    registrar("email", score, email[:150], cat)

# =========================================
# HISTÓRICO
# =========================================

st.header("📊 Histórico SOC")

if historico:
    df = pd.DataFrame(historico)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nenhum evento registrado ainda.")

# =========================================
# PAINEL SOC
# =========================================

st.header("📡 Painel SOC")

total = len(historico)
sus = len([e for e in historico if e.get("score", 0) >= 3])
alert = len([e for e in historico if e.get("score", 0) >= 6])

c1, c2, c3 = st.columns(3)
c1.metric("Eventos detectados", total)
c2.metric("Eventos suspeitos", sus)
c3.metric("Alertas ativos", alert)

# =========================================
# RADAR DE AMEAÇA
# =========================================

st.header("🛰 Radar de ameaça")

if alert >= 4:
    st.error("🚨 Nível alto de ameaça")
elif alert >= 1:
    st.warning("⚠ Atividade suspeita")
else:
    st.success("🟢 Ambiente seguro")

# =========================================
# RANKING
# =========================================

st.header("📈 Ranking de golpes")

if historico:
    df_rank = pd.DataFrame(historico)
    if "categoria" in df_rank.columns:
        ranking = df_rank["categoria"].value_counts().reset_index()
        ranking.columns = ["Categoria", "Quantidade"]
        st.dataframe(ranking, use_container_width=True)
else:
    st.info("Sem dados para ranking ainda.")

# =========================================
# CAMPANHAS
# =========================================

st.header("🚨 Campanhas de golpe")

if historico:
    df_camp = pd.DataFrame(historico)
    if "categoria" in df_camp.columns:
        repetidos = df_camp["categoria"].value_counts()
        encontrou = False

        for tipo, valor in repetidos.items():
            if valor >= 3 and tipo != "baixo_risco":
                encontrou = True
                st.warning(f"Possível campanha ativa: {tipo} ({valor} ocorrências)")

        if not encontrou:
            st.success("Nenhuma campanha forte detectada no momento.")
else:
    st.info("Sem histórico suficiente para campanhas.")

# =========================================
# BIBLIOTECA
# =========================================

st.header("📚 Biblioteca de golpes")

for nome, desc in golpes_conhecidos.items():
    st.write(f"**{nome}** — {desc}")

# =========================================
# CHAT
# =========================================

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
                score_dom, cat_dom, motivos = detectar_dominio_falso(p)
                clones = detectar_site_clone_banco(p)
                resposta = f"""🔎 Análise de domínio

Domínio: {p}
Score: {score_dom}
Categoria: {cat_dom}"""

                if motivos:
                    resposta += f"\nMotivos: {', '.join(motivos)}"

                if clones:
                    resposta += "\n🚨 Possível site clone de banco"

                return resposta

    if score > 0:
        return f"""🚨 Análise do chat

Score: {score}
Categoria: {cat}
Sinais: {", ".join(achados)}"""

    return """🤖 Posso ajudar com:

• analisar IP
• verificar site
• detectar golpes

Exemplos:
analise ip 8.8.8.8
verificar site itau-login-seguro.com
isso é golpe de pix urgente
"""

if chat and not limite_atingido:
    contar_uso()
    resposta = responder_chat(chat)
    st.write(resposta)

    score_chat, cat_chat, _ = classificar_texto(chat)
    registrar("chat", score_chat, chat[:150], cat_chat)
elif chat and limite_atingido:
    st.warning("Ative o premium para continuar usando o chat.")

# =========================================
# RELATÓRIO PDF
# =========================================

st.header("📄 Gerar relatório")

if st.button("Gerar PDF"):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    y = 800
    c.drawString(40, y, "Relatório Escudo Digital IA")
    y -= 30

    for e in historico:
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
