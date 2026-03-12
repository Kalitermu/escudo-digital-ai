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

st.title("🛡️ ESCUDO DIGITAL IA")
st.subheader("SOC de monitoramento de golpes e análise OSINT")

modo_idoso = st.toggle("👵 Modo proteção para idosos", True)

HIST = "historico.json"
MAPA = "mapa_ips.json"

def carregar(arq):
    try:
        with open(arq,"r") as f:
            return json.load(f)
    except:
        return []

def salvar(arq,dados):
    with open(arq,"w") as f:
        json.dump(dados,f)

historico = carregar(HIST)
mapa_ips = carregar(MAPA)

def registrar(tipo,score,detalhe,categoria):
    evento={
        "data":str(datetime.datetime.now()),
        "tipo":tipo,
        "score":score,
        "categoria":categoria,
        "detalhe":detalhe
    }
    historico.append(evento)
    salvar(HIST,historico)

def registrar_ip(ip,lat,lon,pais,isp):
    mapa_ips.append({
        "ip":ip,
        "lat":lat,
        "lon":lon,
        "pais":pais,
        "isp":isp
    })
    salvar(MAPA,mapa_ips)

# INDICADORES DE GOLPES

indicadores={

"phishing_bancario":[
"senha","login","banco","verificação","codigo","código",
"confirme","conta bloqueada","segurança","acesso"
],

"golpe_pix":[
"pix","chave pix","transferência","transferencia",
"pix urgente","manda pix","pagamento imediato"
],

"emprestimo_falso":[
"empréstimo","emprestimo","pré-aprovado","pre-aprovado",
"crédito","credito","taxa","liberação","liberacao",
"valor aprovado","oferta","veiculo em garantia"
],

"extorsao":[
"facção","pcc","cv","comando",
"estamos monitorando",
"sua família","sua familia",
"se não pagar",
"pague agora",
"resolva isso agora"
],

"engenharia_social":[
"urgente","agora","hoje","imediatamente",
"clique aqui","última chance","nao perca"
]

}

def classificar(texto):

    texto=texto.lower()
    score=0
    achados=[]
    categorias=[]

    for categoria,palavras in indicadores.items():

        for p in palavras:
            if p in texto:
                score+=2
                achados.append(p)
                categorias.append(categoria)

    if "830000" in texto or "200000" in texto:
        score+=3
        achados.append("valor alto")

    categoria_final="baixo_risco"

    if "extorsao" in categorias:
        categoria_final="possivel_extorsao"

    elif "emprestimo_falso" in categorias:
        categoria_final="possivel_emprestimo_falso"

    elif "golpe_pix" in categorias:
        categoria_final="possivel_golpe_pix"

    elif "phishing_bancario" in categorias:
        categoria_final="possivel_phishing_bancario"

    return score,categoria_final,achados

def defesa(cat):

    base=[
    "Não clique em links da mensagem",
    "Confirme no site oficial",
    "Não envie senha ou Pix",
    "Peça ajuda a alguém de confiança"
    ]

    extras={

    "possivel_emprestimo_falso":[
    "Bancos não cobram taxa para liberar empréstimo",
    "Promessas de crédito fácil são suspeitas"
    ],

    "possivel_golpe_pix":[
    "Golpistas usam urgência para forçar Pix"
    ],

    "possivel_extorsao":[
    "Golpistas usam ameaça para causar medo",
    "Não faça pagamentos",
    "Bloqueie o número",
    "Registre ocorrência"
    ]
    }

    return base+extras.get(cat,[])

def mostrar(score,cat,achados):

    if score>=6:
        st.error("🚨 Alto risco de golpe")

    elif score>=3:
        st.warning("⚠ Conteúdo suspeito")

    else:
        st.success("🟢 Baixo risco")

    st.write("Score:",score)
    st.write("Categoria:",cat)

    if achados:
        st.write("Sinais:",",".join(achados))

    st.markdown("### 🛡 Defesa recomendada")

    for d in defesa(cat):
        st.write("-",d)

    if modo_idoso and cat!="baixo_risco":
        st.markdown("### 👵 Orientação simples")
        st.write("⚠ Isso pode ser golpe")
        st.write("Não mande dinheiro")
        st.write("Não clique em links")
        st.write("Peça ajuda a um familiar")

# OSINT IP

st.header("🌍 Análise OSINT de IP")

ip=st.text_input("Digite domínio ou IP")

if st.button("Analisar IP"):

    r=requests.get(f"http://ip-api.com/json/{ip}").json()

    if r["status"]=="success":

        pais=r["country"]
        cidade=r["city"]
        isp=r["isp"]
        lat=r["lat"]
        lon=r["lon"]

        st.write("País:",pais)
        st.write("Cidade:",cidade)
        st.write("ISP:",isp)

        registrar("ip",1,ip,"osint_ip")
        registrar_ip(ip,lat,lon,pais,isp)

        mapa=folium.Map(location=[lat,lon],zoom_start=4)

        folium.Marker(
        [lat,lon],
        popup=f"IP:{ip} {pais}"
        ).add_to(mapa)

        st_folium(mapa,width=700,height=400)

# RADAR GLOBAL

st.header("🌎 Radar global de ameaças")

if mapa_ips:

    mapa=folium.Map(location=[0,0],zoom_start=2)

    for item in mapa_ips:

        lat=item.get("lat")
        lon=item.get("lon")

        if lat and lon:

            folium.CircleMarker(
            location=[lat,lon],
            radius=6,
            color="red",
            fill=True,
            popup=item["ip"]
            ).add_to(mapa)

    st_folium(mapa,width=900,height=500)

# DETECTOR DE PHISHING

st.header("🚨 Detector de Phishing")

msg=st.text_area("Cole mensagem suspeita")

if st.button("Analisar mensagem"):

    score,cat,achados=classificar(msg)
    mostrar(score,cat,achados)

    registrar("mensagem",score,msg[:120],cat)

# DOMINIO

st.header("🔎 Scanner de domínio")

dom=st.text_input("Digite URL suspeita")

if st.button("Analisar domínio"):

    score=0

    if "login" in dom or "secure" in dom:
        score=2

    if "google" in dom and dom!="google.com":
        score+=3

    if score>=3:
        st.error("🚨 Domínio suspeito")

    else:
        st.success("🟢 Domínio aparentemente seguro")

    registrar("dominio",score,dom,"analise_dominio")

# OCR

st.header("📷 Analisar print de golpe")

arq=st.file_uploader("Envie print",type=["png","jpg","jpeg"])

if arq:

    img=Image.open(arq)
    st.image(img)

    if OCR_OK:

        texto=pytesseract.image_to_string(img)

        st.write("Texto detectado:")
        st.write(texto)

        score,cat,achados=classificar(texto)

        mostrar(score,cat,achados)

        registrar("imagem",score,texto[:120],cat)

# EMAIL

st.header("📧 Analisar email suspeito")

email=st.text_area("Cole o email")

if st.button("Analisar email"):

    score,cat,achados=classificar(email)

    mostrar(score,cat,achados)

    registrar("email",score,email[:120],cat)

# HISTORICO

st.header("📊 Histórico SOC")

if historico:
    st.dataframe(pd.DataFrame(historico))

# PAINEL

st.header("📡 Painel SOC")

total=len(historico)
sus=len([e for e in historico if e["score"]>=3])
alert=len([e for e in historico if e["score"]>=6])

c1,c2,c3=st.columns(3)

c1.metric("Eventos detectados",total)
c2.metric("Eventos suspeitos",sus)
c3.metric("Alertas ativos",alert)

# RADAR

st.header("🛰 Radar de ameaça")

if alert>=4:
    st.error("🚨 Nível alto de ameaça")

elif alert>=1:
    st.warning("⚠ Atividade suspeita")

else:
    st.success("🟢 Ambiente seguro")

# CHAT

st.header("🤖 Chat do Escudo")

chat=st.text_input("Pergunte algo")

if chat:

    score,cat,achados=classificar(chat)

    st.write("Análise:")
    st.write("Score:",score)
    st.write("Categoria:",cat)

# RELATORIO

st.header("📄 Gerar relatório")

if st.button("Gerar PDF"):

    buffer=io.BytesIO()

    c=canvas.Canvas(buffer)

    y=800

    for e in historico:

        linha=f"{e['data']} {e['tipo']} score:{e['score']}"

        c.drawString(40,y,linha[:90])

        y-=20

        if y<60:
            c.showPage()
            y=800

    c.save()

    st.download_button(
    "Baixar relatório",
    buffer.getvalue(),
    "relatorio_soc.pdf"
    )
