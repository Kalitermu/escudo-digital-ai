import re
import tempfile
import numpy as np
import streamlit as st
from PIL import Image
import cv2

st.set_page_config(page_title="ESCUDO DIGITAL IA", layout="centered")

# ---------- UI/STYLE ----------
st.markdown("""
<style>
  .card{padding:14px 14px;border:1px solid rgba(255,255,255,.08);border-radius:16px;background:rgba(255,255,255,.03)}
  .muted{opacity:.8}
  .big{font-size:28px;font-weight:800;margin:0}
  .pill{display:inline-block;padding:6px 10px;border-radius:999px;border:1px solid rgba(255,255,255,.12);margin-right:6px}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ ESCUDO DIGITAL IA")
st.caption("Detector de golpes + alerta de conteúdo gerado por IA (triagem automática com explicação).")

tab1, tab2, tab3 = st.tabs(["✉️ Texto", "📷 Print", "🎞️ Vídeo"])

# ---------- RULES ----------
SHORTENERS = {"bit.ly","tinyurl.com","t.co","cutt.ly","is.gd","rebrand.ly","shorte.st","ow.ly","lnkd.in"}
URL_RE = re.compile(r"(https?://[^\s]+)|(\bwww\.[^\s]+)", re.IGNORECASE)

URG = ["urgente","agora","imediato","última chance","ultima chance","expira","bloquead","suspens","cancelad","multa","processo"]
PAY = ["pix","boleto","transferência","transferencia","depósito","deposito","taxa","pagamento","pague","cobrança","cobranca","estorno","reembolso","premio","prêmio"]
DATA = ["senha","código","codigo","token","sms","whatsapp","2fa","cpf","rg","cartão","cartao","cvv","login","e-mail","email","conta","banco"]
SOCIAL = ["clique","acesse","entre","confirme","atualize","valide","cadastro"]

IA_HINTS = ["como modelo de linguagem","sou uma ia","gerado por ia","assistente virtual"]

def extract_urls(text: str):
    urls = []
    for m in URL_RE.finditer(text or ""):
        u = m.group(0)
        if u:
            if u.lower().startswith("www."):
                u = "http://" + u
            urls.append(u.strip("()[]{}<>.,;!"))
    # unique preserving order
    out = []
    seen = set()
    for u in urls:
        if u not in seen:
            out.append(u); seen.add(u)
    return out

def domain_of(url: str) -> str:
    m = re.search(r"^(?:https?://)?([^/]+)", url.strip(), re.IGNORECASE)
    dom = (m.group(1).lower() if m else "")
    return dom.replace("www.", "")

def looks_like_ip(dom: str) -> bool:
    return bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", dom))

def weird_tld(dom: str) -> bool:
    common = (".com",".com.br",".br",".org",".net",".gov.br",".edu",".io",".app")
    return not any(dom.endswith(x) for x in common)

def hit_list(text: str, words):
    t = (text or "").lower()
    return [w for w in words if w in t]

def scam_score(text: str):
    t = (text or "").lower()
    findings = []
    score = 0

    h1 = hit_list(text, URG)
    h2 = hit_list(text, PAY)
    h3 = hit_list(text, DATA)
    h4 = hit_list(text, SOCIAL)
    urls = extract_urls(text)

    if h1: score += 25; findings.append(f"⚠️ Urgência/ameaça: {', '.join(h1[:6])}")
    if h2: score += 25; findings.append(f"💸 Pagamento/dinheiro: {', '.join(h2[:6])}")
    if h3: score += 20; findings.append(f"🔐 Pedido de dados/códigos: {', '.join(h3[:6])}")
    if h4: score += 10; findings.append(f"🖱️ Ação forçada (clique/confirmar): {', '.join(h4[:6])}")

    if urls:
        score += 10
        findings.append(f"🔗 Links detectados: {len(urls)}")

        for u in urls[:8]:
            dom = domain_of(u)
            if dom in SHORTENERS:
                score += 20; findings.append(f"⛔ Link encurtado: {dom}")
            if looks_like_ip(dom):
                score += 25; findings.append(f"⛔ Link com IP direto: {dom}")
            if weird_tld(dom):
                score += 10; findings.append(f"⚠️ Domínio estranho: {dom}")

    if not findings:
        findings = ["✅ Poucos sinais clássicos de golpe detectados (mesmo assim, confirme pelos canais oficiais)."]

    return min(100, score), findings, urls

def ia_text_score(text: str):
    if not (text or "").strip():
        return 0, ["Sem texto para avaliar."]
    t = text.strip()
    low = t.lower()
    reasons = []

    words = re.findall(r"\w+", t, re.UNICODE)
    avg_len = sum(len(w) for w in words)/max(1,len(words))

    score = 0
    if any(h in low for h in IA_HINTS):
        score += 60; reasons.append("Frase típica de IA detectada.")
    if avg_len >= 6:
        score += 15; reasons.append("Palavras mais longas em média (texto mais 'formal').")
    if len(t) >= 600:
        score += 10; reasons.append("Texto muito longo e estruturado.")
    if len(re.findall(r"[;:]", t)) >= 4:
        score += 10; reasons.append("Pontuação/estrutura muito 'certinha'.")

    if not reasons:
        reasons = ["Poucos sinais de texto 'robótico' nesta triagem."]
    return min(100, score), reasons

def risk_label(score: int):
    if score >= 80: return "🔴 CRÍTICO"
    if score >= 60: return "🟠 ALTO"
    if score >= 30: return "🟡 MÉDIO"
    return "🟢 BAIXO"

# ---------- VIDEO HEURISTICS ----------
def extract_frames(video_path: str, max_frames=12):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    idxs = np.linspace(0, max(total-1, 0), num=max_frames, dtype=int).tolist() if total > 0 else list(range(max_frames))

    frames = []
    cur = 0
    pick = set(idxs)
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        if cur in pick:
            frames.append(fr)
        cur += 1
        if len(frames) >= max_frames:
            break
    cap.release()
    return frames

def frame_metrics(frame_bgr):
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    sharp = cv2.Laplacian(gray, cv2.CV_64F).var()
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    noise = float(np.mean(np.abs(gray.astype(np.float32) - blur.astype(np.float32))))
    return sharp, noise

def ai_video_score(video_path: str):
    frames = extract_frames(video_path, max_frames=12)
    if not frames:
        return None, ["Não consegui ler o vídeo. Tente MP4 menor."], {}

    sharps, noises = [], []
    for fr in frames:
        s, n = frame_metrics(fr)
        sharps.append(s); noises.append(n)

    sharp_med = float(np.median(sharps))
    noise_med = float(np.median(noises))
    var_sharp = float(np.var(sharps))

    score = 0
    reasons = []
    if sharp_med < 55:
        score += 20; reasons.append("Nitidez baixa (pode indicar reprocessamento).")
    if noise_med < 5.5:
        score += 15; reasons.append("Textura muito lisa (pode ser filtragem/IA).")
    if var_sharp > 2500:
        score += 15; reasons.append("Oscilação de nitidez entre frames (possível re-render/edição).")

    verdict = "🚨 SUSPEITA (IA/edição)" if score >= 35 else "✅ Sem sinais fortes (triagem)"
    if not reasons:
        reasons = ["Sem sinais fortes detectados nesta análise leve."]
    return min(100, score), reasons, {"nitidez_mediana": round(sharp_med,2), "textura_mediana": round(noise_med,2), "var_nitidez": round(var_sharp,2), "frames": len(frames), "veredito": verdict}

# ---------- TAB 1: TEXT ----------
with tab1:
    text = st.text_area("Cole a mensagem suspeita:", height=160, placeholder="WhatsApp / e-mail / SMS…")
    if st.button("ANALISAR TEXTO 🔎", use_container_width=True):
        if not text.strip():
            st.warning("Cole uma mensagem primeiro.")
        else:
            s, findings, urls = scam_score(text)
            lvl = risk_label(s)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f'<p class="big">Risco de golpe: {s}/100 — {lvl}</p>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("### Por que?")
            for f in findings:
                st.write("- " + f)

            if urls:
                st.markdown("### Links encontrados")
                for u in urls:
                    st.write("• " + u)

            ai_s, ai_r = ia_text_score(text)
            st.markdown("---")
            st.markdown("### Detector de IA (texto)")
            st.write(f"**Score IA:** {ai_s}/100")
            for r in ai_r:
                st.write("• " + r)

# ---------- TAB 2: PRINT ----------
with tab2:
    img_file = st.file_uploader("Envie um print (PNG/JPG)", type=["png","jpg","jpeg"])
    st.caption("Obs: leitura de texto do print (OCR) pesado não está ativado aqui pra manter rápido e estável.")
    if img_file:
        img = Image.open(img_file).convert("RGB")
        st.image(img, use_container_width=True)
        st.info("Se você quiser OCR real no print, eu ativo na próxima versão (com tesseract e extração automática).")

# ---------- TAB 3: VIDEO ----------
with tab3:
    vid = st.file_uploader("Envie um vídeo (MP4/MOV)", type=["mp4","mov","avi","mkv"])
    if vid:
        st.video(vid)
        if st.button("ANALISAR VÍDEO 🎞️", use_container_width=True):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(vid.getbuffer())
                path = tmp.name
            score, reasons, metrics = ai_video_score(path)
            if score is None:
                st.error(reasons[0])
            else:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f'<p class="big">Alerta IA (vídeo): {score}/100 — {metrics["veredito"]}</p>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("### Por que?")
                for r in reasons:
                    st.write("• " + r)
                st.caption(f"Métricas: {metrics}")

st.divider()
st.markdown("### ✅ Funcionalidades")
st.write("• Texto: score de golpe + explicação + links suspeitos")
st.write("• Print: upload (na próxima versão ativamos OCR automático)")
st.write("• Vídeo: triagem leve para sinais de IA/edição (heurística)")
st.caption("⚠️ Detecção de IA/deepfake é probabilística. Use como alerta, não como prova.")
cat >> app.py << 'EOF'

# ==========================
# 🧠 IA VIVA (memória leve)
# ==========================
try:
    import json, os

    hist_file = "historico.json"

    if os.path.exists(hist_file):
        with open(hist_file, "r", encoding="utf-8") as h:
            hist = json.load(h)

        ultimos = hist[:10] if isinstance(hist, list) else []

        repeticoes = 0
        for ev in ultimos:
            txt = str(ev.get("preview", "")).lower()
            if any(w in txt for w in ["pix","banco","codigo","verificacao"]):
                repeticoes += 1

        if repeticoes >= 3:
            st.info("🧠 IA detectou padrão recorrente.")
except:
    pass


# ==========================
# 🎞️ TRIAGEM IA EM VÍDEO
# ==========================
st.subheader("🎞️ Vídeo (triagem IA)")

vid = st.file_uploader("Envie um vídeo", type=["mp4","mov","avi"])

if vid:
    nome = vid.name.lower()

    score_video = 15
    motivos = []

    if any(w in nome for w in ["ai","deepfake","faceswap","fake"]):
        score_video += 40
        motivos.append("Nome do arquivo sugere conteúdo gerado por IA.")

    if vid.size < 500000:
        score_video += 20
        motivos.append("Arquivo muito pequeno (possível render IA).")

    score_video = max(0, min(100, score_video))

    st.progress(score_video)
    st.write(f"🎯 Chance de ser IA: {score_video}/100")

    for m in motivos:
        st.write("•", m)

    if score_video >= 60:
        st.warning("⚠️ Possível vídeo gerado por IA")
    else:
        st.success("✅ Sem sinais fortes de IA")


# ==========================
# 🛰️ SOC ELITE - VIDEO ANALYZER
# ==========================
st.subheader("🛰️ SOC ELITE — Análise de Vídeo")

video = st.file_uploader("🎞️ Envie um vídeo para triagem IA", type=["mp4","mov","avi"])

if video:

    st.video(video)

    nome = video.name.lower()
    tamanho = video.size

    score = 20
    motivos = []

    # sinais comuns IA
    if any(w in nome for w in ["ai","deepfake","faceswap","fake","render"]):
        score += 35
        motivos.append("Nome do arquivo contém termos ligados a IA.")

    if tamanho < 800000:
        score += 20
        motivos.append("Arquivo pequeno demais para vídeo real.")

    if tamanho > 50000000:
        score += 10
        motivos.append("Compressão ou renderização suspeita.")

    score = max(0, min(100, score))

    st.progress(score)

    st.markdown("### 🧾 Resultado SOC")

    if score >= 70:
        st.error(f"🔴 POSSÍVEL IA ({score}/100)")
    elif score >= 40:
        st.warning(f"🟠 SUSPEITO ({score}/100)")
    else:
        st.success(f"🟢 SEM SINAIS FORTES ({score}/100)")

    with st.expander("📌 Motivos detectados"):
        if motivos:
            for m in motivos:
                st.write("•", m)
        else:
            st.write("• Nenhum padrão forte detectado.")

