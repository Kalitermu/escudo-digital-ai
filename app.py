import streamlit as st
from PIL import Image
import pytesseract
import re
from urllib.parse import urlparse

# ====== CONFIG ======
st.set_page_config(page_title="Escudo Digital IA", layout="centered")

# Coloque aqui seu link REAL depois (Stripe Payment Link ou Mercado Pago)
CHECKOUT_URL = "https://SEU-LINK-DE-PAGAMENTO-AQUI"

# ====== LOGIN PREMIUM SIMPLES (MVP) ======
if "premium" not in st.session_state:
    st.session_state.premium = False

st.title("🛡️ ESCUDO DIGITAL IA")
st.caption("Análise automática de mensagens, e-mails e links — com explicação clara.")

with st.expander("💎 Premium"):
    if st.session_state.premium:
        st.success("Premium ATIVO ✅")
        if st.button("Desativar (teste)"):
            st.session_state.premium = False
    else:
        st.info("Premium bloqueia limites e libera relatório + histórico.")
        st.link_button("Assinar Premium (Pix/Cartão)", CHECKOUT_URL)
        # Botão de teste só pra você desenvolver sem pagar
        if st.button("Ativar Premium (TESTE)"):
            st.session_state.premium = True

st.divider()

# ====== APP ======
auto = st.toggle("⚡ Analisar automaticamente", value=True)
texto = st.text_area("✉️ Cole mensagem, e-mail ou link:", height=180)

uploaded_file = st.file_uploader("📷 Enviar PRINT", type=["png","jpg","jpeg"])
if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, use_column_width=True)
    texto_img = pytesseract.image_to_string(img)
    st.code(texto_img)
    texto = (texto + " " + texto_img).strip()

SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "rebrand.ly", "goo.gl"}

def find_urls(t: str):
    raw = re.findall(r'https?://\S+|www\.\S+', t, flags=re.IGNORECASE)
    out = []
    seen = set()
    for u in raw:
        u = u.strip().rstrip(").,;!?:]}")
        if u.lower().startswith("www."):
            u = "http://" + u
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out

def domain_of(url: str):
    d = urlparse(url).netloc.lower()
    return d[4:] if d.startswith("www.") else d

def analyze(t: str):
    t = t.lower()
    score = 0
    motivos = []
    regras = {
        "pix":18, "transferencia":18, "urgente":16, "senha":25,
        "login":16, "confirmar":14, "clique":12, "bloqueado":18
    }
    for k,v in regras.items():
        if k in t:
            score += v
            motivos.append(k)

    urls = find_urls(t)
    url_flags = []
    for u in urls:
        dom = domain_of(u)
        flags = []
        if dom in SHORTENERS:
            score += 30; flags.append("encurtado")
        if any(x in u for x in ["login","verify","secure","account","update"]):
            score += 15; flags.append("palavras phishing")
        url_flags.append((u, dom, flags))

    score = min(score, 100)
    return score, sorted(set(motivos)), url_flags

run = (auto and bool(texto.strip())) or st.button("🔎 Analisar agora")

if run and texto.strip():
    score, motivos, url_flags = analyze(texto)

    st.subheader("📊 Resultado")
    st.progress(score/100)
    st.metric("Score de Risco", f"{score}/100")

    if score >= 70:
        st.error("🚨 RISCO ALTO")
    elif score >= 40:
        st.warning("⚠️ RISCO MÉDIO")
    else:
        st.success("🟢 RISCO BAIXO")

    st.subheader("🧠 Motivos")
    st.write(", ".join(motivos) if motivos else "Nenhum sinal forte.")

    if url_flags:
        st.subheader("🔗 Links detectados (não clicáveis)")
        for u, dom, flags in url_flags:
            st.code(u)
            if flags:
                st.warning(f"Suspeito: {' | '.join(flags)} — domínio: {dom}")
            else:
                st.success(f"Sem sinais óbvios — domínio: {dom}")

    # ====== PREMIUM: relatório ======
    st.divider()
    if st.session_state.premium:
        st.subheader("🧾 Relatório Premium")
        rel = f"""Escudo Digital IA — Relatório
Score: {score}/100
Status: {'ALTO' if score>=70 else 'MÉDIO' if score>=40 else 'BAIXO'}
Motivos: {', '.join(motivos) if motivos else 'nenhum'}
"""
        st.download_button("Baixar relatório (.txt)", rel, file_name="relatorio_escudo.txt")
    else:
        st.info("Relatório detalhado é Premium. Use o botão 'Assinar Premium'.")
