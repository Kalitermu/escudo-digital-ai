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
except:
    OCR_OK = False

st.set_page_config(page_title="Escudo Digital IA", layout="wide")

# =========================
# TEMA VISUAL
# =========================

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
</style>
""", unsafe_allow_html=True)

st.title("🛡️ ESCUDO DIGITAL IA")
st.subheader("SOC de monitoramento de golpes e análise OSINT")

modo_idoso = st.toggle("👵 Modo proteção para idosos", value=True)

# =========================
# ARQUIVOS
# =========================

HIST_ARQ = "historico.json"
MAPA_ARQ = "mapa_ips.json"

def carregar_json(nome):
    try:
        with open(nome, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def salvar_json(nome, dados):
    with open(nome, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

historico = carregar_json(HIST_ARQ)
mapa_ips = carregar_json(MAPA_ARQ)

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

# =========================
# BASES DE REGRAS
# =========================

sites_legitimos = [
    "google.com",
    "facebook.com",
    "instagram.com",
    "paypal.com",
    "amazon.com",
    "bradesco.com.br",
    "itau.com.br",
    "nubank.com.br",
    "mercadolivre.com.br",
    "gov.br",
    "caixa.gov.br",
    "bb.com.br",
    "santander.com.br"
]

indicadores = {
    "phishing_bancario": [
        "senha", "login", "banco", "verificação", "codigo", "código",
        "confirme", "conta bloqueada", "segurança", "acesso"
    ],
    "golpe_pix": [
        "pix", "chave pix", "bloqueado", "transferência", "transferencia",
        "comprovante", "estorno", "pagamento"
    ],
    "emprestimo_falso": [
        "empréstimo", "emprestimo", "pré-aprovado", "pre-aprovado",
        "crédito", "credito", "taxa", "liberação", "liberacao",
        "valor aprovado", "oferta", "veículo em garantia",
        "veiculo em garantia", "parcelas"
    ],
    "engenharia_social": [
        "urgente", "agora", "hoje", "imediatamente", "clique aqui",
        "última chance", "ultima chance", "não perca", "nao perca"
    ],
    "golpe_idoso": [
        "aposentado", "aposentadoria", "benefício", "beneficio",
        "consignado"
    ]
}

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

            if categoria in ["emprestimo_falso", "phishing_bancario", "golpe_pix", "golpe_idoso"]:
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

    if "emprestimo_falso" in categorias:
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

    tokens_suspeitos = ["login", "secure", "verify", "update", "account", "confirm"]

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

def defesa_recomendada(categoria):
    base = [
        "Não clique em links ou números enviados na própria mensagem.",
        "Confirme a informação pelo site ou aplicativo oficial.",
        "Não envie senha, código, Pix ou documento por impulso.",
        "Peça ajuda a alguém de confiança antes de tomar decisão financeira."
    ]

    extras = {
        "possivel_emprestimo_falso": [
            "Bancos sérios não cobram taxa antecipada para liberar empréstimo.",
            "Promessa de valor alto pré-aprovado é sinal de alerta.",
            "Peça CNPJ e confirme se a empresa existe em canais oficiais."
        ],
        "possivel_golpe_pix": [
            "Golpistas usam urgência para forçar Pix rápido.",
            "Nunca faça transferência sem confirmar fora da conversa."
        ],
        "possivel_phishing_bancario": [
            "Nunca digite senha após clicar em link recebido por mensagem."
        ],
        "engenharia_social": [
            "Pare e confirme a história antes de agir."
        ],
        "dominio_suspeito": [
            "Digite o endereço do site manualmente no navegador."
        ],
        "possivel_golpe_financeiro": [
            "Golpes financeiros costumam ser mais perigosos para idosos e familiares."
        ]
    }

    saida = base[:]
    saida.extend(extras.get(categoria, []))
    return saida

def exibir_defesa(categoria):
    dicas = defesa_recomendada(categoria)
    html = "<div class='caixa-defesa'><b>🛡 Defesa recomendada</b><ul>"
    for d in dicas:
        html += f"<li>{d}</li>"
    html += "</ul></div>"
    st.markdown(html, unsafe_allow_html=True)

def exibir_modo_idoso(categoria):
    if not modo_idoso:
        return

    mensagem = """
<div class='caixa-idoso'>
<b>👵 Orientação simples</b><br><br>
⚠ Isso pode ser golpe.<br>
Não mande dinheiro.<br>
Não clique em link.<br>
Peça ajuda para um familiar ou pessoa de confiança.
</div>
"""
    if categoria != "baixo_risco":
        st.markdown(mensagem, unsafe_allow_html=True)

def mostrar_resultado(score, categoria, achados):
    if score >= 6:
        st.error("🚨 Alto risco de golpe")
    elif score >= 3:
        st.warning("⚠️ Conteúdo suspeito")
    else:
        st.success("🟢 Baixo risco")

    st.write("**Score:**", score)
    st.write("**Categoria provável:**", categoria.replace("_", " "))

    if achados:
        st.write("**Sinais encontrados:**", ", ".join(achados))

    exibir_defesa(categoria)
    exibir_modo_idoso(categoria)

# =========================
# OSINT IP
# =========================

st.header("🌍 Análise OSINT de IP")

ip = st.text_input("Digite domínio ou IP")

if st.button("Analisar IP"):
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

            registrar("ip", 1, ip, "osint_ip", "Verificar reputação e contexto do IP.")

            if lat and lon:
                registrar_ip(ip, lat, lon, pais, isp)

                mapa = folium.Map(location=[lat, lon], zoom_start=4)
                folium.Marker(
                    [lat, lon],
                    popup=f"IP: {ip}<br>País: {pais}<br>ISP: {isp}",
                    tooltip="Clique para detalhes"
                ).add_to(mapa)

                st_folium(mapa, width=700, height=450)
        else:
            st.error("Não foi possível localizar o IP")

    except:
        st.error("Erro na consulta")

# =========================
# RADAR GLOBAL
# =========================

st.header("🌎 Radar global de ameaças")

if mapa_ips:
    mapa_global = folium.Map(location=[0, 0], zoom_start=2)

    for item in mapa_ips:
        ip_item = item.get("ip", "?")
        pais = item.get("pais", "desconhecido")
        isp = item.get("isp", "desconhecido")
        lat = item.get("lat")
        lon = item.get("lon")

        if lat and lon:
            folium.CircleMarker(
                location=[lat, lon],
                radius=6,
                color="red",
                fill=True,
                popup=f"IP: {ip_item}<br>País: {pais}<br>ISP: {isp}"
            ).add_to(mapa_global)

    st_folium(mapa_global, width=900, height=500)
else:
    st.info("Nenhum IP analisado ainda.")

# =========================
# PHISHING
# =========================

st.header("🚨 Detector de Phishing")

msg = st.text_area("Cole mensagem suspeita")

if st.button("Analisar mensagem"):
    score, categoria, achados = classificar_texto(msg)
    mostrar_resultado(score, categoria, achados)

    defesa_txt = " | ".join(defesa_recomendada(categoria))
    registrar("mensagem", score, msg[:150], categoria, defesa_txt)

# =========================
# DOMÍNIO
# =========================

st.header("🔎 Scanner de domínio")

dominio = st.text_input("Digite URL suspeita")

if st.button("Analisar domínio"):
    score_dom, categoria_dom, motivos = detectar_dominio_falso(dominio)

    if score_dom >= 3:
        st.error("🚨 Domínio muito suspeito")
    elif score_dom >= 1:
        st.warning("⚠️ Domínio suspeito")
    else:
        st.success("🟢 Domínio aparentemente seguro")

    st.write("**Score do domínio:**", score_dom)
    if motivos:
        st.write("**Motivos:**", ", ".join(motivos))

    exibir_defesa(categoria_dom)
    exibir_modo_idoso(categoria_dom)

    defesa_txt = " | ".join(defesa_recomendada(categoria_dom))
    registrar("dominio", score_dom if score_dom > 0 else 1, dominio, categoria_dom, defesa_txt)

# =========================
# OCR
# =========================

st.header("📷 Analisar print de golpe")

arquivo = st.file_uploader("Envie print", type=["png", "jpg", "jpeg"])

if arquivo:
    img = Image.open(arquivo)
    st.image(img)

    if OCR_OK:
        try:
            texto = pytesseract.image_to_string(img)

            st.write("Texto detectado:")
            st.write(texto)

            score, categoria, achados = classificar_texto(texto)
            mostrar_resultado(score, categoria, achados)

            defesa_txt = " | ".join(defesa_recomendada(categoria))
            registrar("imagem", score if score > 0 else 1, texto[:150], categoria, defesa_txt)

        except:
            st.warning("OCR não disponível")
    else:
        st.warning("OCR não disponível no servidor")

# =========================
# EMAIL
# =========================

st.header("📧 Analisar email suspeito")

email = st.text_area("Cole o email")

if st.button("Analisar email"):
    score, categoria, achados = classificar_texto(email)
    mostrar_resultado(score, categoria, achados)

    defesa_txt = " | ".join(defesa_recomendada(categoria))
    registrar("email", score, email[:150], categoria, defesa_txt)

# =========================
# HISTÓRICO
# =========================

st.header("📊 Histórico SOC")

if historico:
    df = pd.DataFrame(historico)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nenhum evento registrado ainda.")

# =========================
# PAINEL
# =========================

st.header("📡 Painel SOC")

eventos = len(historico)
suspeitos = len([e for e in historico if e.get("score", 0) >= 3])
alertas = len([e for e in historico if e.get("score", 0) >= 6])

c1, c2, c3 = st.columns(3)
c1.metric("Eventos detectados", eventos)
c2.metric("Eventos suspeitos", suspeitos)
c3.metric("Alertas ativos", alertas)

# =========================
# RADAR
# =========================

st.header("🛰️ Radar de ameaça")

if alertas >= 5:
    st.error("🚨 Nível alto de ameaça")
elif alertas >= 1:
    st.warning("⚠️ Atividade suspeita")
else:
    st.success("🟢 Ambiente seguro")

# =========================
# CHAT
# =========================

st.header("🤖 Chat do Escudo")

pergunta = st.text_input("Pergunte algo ou peça análise")

def responder_chat(msg_chat):
    texto = msg_chat.lower()

    if "ip" in texto:
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
ASN: {r.get('as')}
"""
                except:
                    return "Não consegui analisar esse IP."

    if "site" in texto or "link" in texto or "." in texto:
        partes = texto.split()
        for p in partes:
            if "." in p:
                score_dom, categoria_dom, motivos = detectar_dominio_falso(p)
                return f"""🔎 Análise de domínio

Domínio: {p}
Score: {score_dom}
Categoria: {categoria_dom.replace("_", " ")}
Motivos: {", ".join(motivos) if motivos else "nenhum sinal forte"}
"""

    if "golpe" in texto or "mensagem" in texto or "pix" in texto or "empréstimo" in texto or "emprestimo" in texto:
        score, categoria, achados = classificar_texto(texto)
        return f"""🚨 Análise do chat

Score: {score}
Categoria: {categoria.replace("_", " ")}
Sinais: {", ".join(achados) if achados else "nenhum"}
"""

    return """🤖 Posso ajudar com:

• analisar IP
• verificar site
• identificar golpe

Exemplos:
analise ip 8.8.8.8
verificar site google-login-secure.com
isso é golpe de pix urgente
"""

if pergunta:
    resposta = responder_chat(pergunta)
    st.write(resposta)

# =========================
# RELATÓRIO PDF
# =========================

st.header("📄 Gerar relatório")

if st.button("Gerar PDF"):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    y = 800
    c.drawString(50, y, "Relatório Escudo Digital IA")
    y -= 35

    for e in historico:
        linha = f"{e.get('data')} | {e.get('tipo')} | {e.get('categoria','')} | score:{e.get('score')}"
        c.drawString(50, y, linha[:110])
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
