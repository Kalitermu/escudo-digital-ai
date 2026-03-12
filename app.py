import streamlit as st
import requests
import pandas as pd
import json
import datetime
import io
from PIL import Image
from reportlab.pdfgen import canvas
import folium
from streamlit_folium import st_folium

try:
    import pytesseract
    OCR_OK=True
except:
    OCR_OK=False


st.set_page_config(page_title="Escudo Digital IA",layout="wide")


# =========================
# TEMA MAIS SUAVE
# =========================

st.markdown("""
<style>

.stApp{
background: linear-gradient(135deg,#e8f0f7,#cfe3f5);
color:#0f172a;
}

h1,h2,h3{
color:#0ea5e9;
}

/* Inputs */

input{
background:white !important;
color:black !important;
border-radius:8px !important;
}

/* textarea */

textarea{
background:white !important;
color:black !important;
}

/* botões */

.stButton>button{
background:linear-gradient(90deg,#0ea5e9,#38bdf8);
border-radius:10px;
color:white;
font-weight:bold;
}

/* métricas */

[data-testid="stMetricValue"]{
color:#0f172a !important;
font-size:30px;
}

[data-testid="stMetricLabel"]{
color:#0369a1 !important;
}

</style>
""",unsafe_allow_html=True)


st.title("🛡️ ESCUDO DIGITAL IA")
st.subheader("SOC de monitoramento de golpes e análise OSINT")


# =========================
# HISTÓRICO
# =========================

try:
    with open("historico.json","r") as f:
        historico=json.load(f)
except:
    historico=[]

try:
    with open("mapa_ips.json","r") as f:
        mapa_ips=json.load(f)
except:
    mapa_ips=[]


def registrar(tipo,score,detalhe=""):

    evento={
        "data":str(datetime.datetime.now()),
        "tipo":tipo,
        "score":score,
        "detalhe":detalhe
    }

    historico.append(evento)

    with open("historico.json","w") as f:
        json.dump(historico,f)


def registrar_ip(ip,lat,lon,pais,isp):

    mapa_ips.append({
        "ip":ip,
        "lat":lat,
        "lon":lon,
        "pais":pais,
        "isp":isp
    })

    with open("mapa_ips.json","w") as f:
        json.dump(mapa_ips,f)


# =========================
# OSINT IP
# =========================

st.header("🌍 Análise OSINT de IP")

ip=st.text_input("Digite domínio ou IP")

if st.button("Analisar IP"):

    try:

        r=requests.get(f"http://ip-api.com/json/{ip}").json()

        pais=r.get("country")
        cidade=r.get("city")
        isp=r.get("isp")

        st.success("Consulta realizada")

        st.write("IP:",ip)
        st.write("País:",pais)
        st.write("Cidade:",cidade)
        st.write("ISP:",isp)
        st.write("ASN:",r.get("as"))

        registrar("ip",1,ip)

        lat=r.get("lat")
        lon=r.get("lon")

        if lat and lon:

            registrar_ip(ip,lat,lon,pais,isp)

            mapa=folium.Map(
                location=[lat,lon],
                zoom_start=4
            )

            folium.Marker(
                [lat,lon],
                popup=f"""
                IP: {ip}<br>
                País: {pais}<br>
                ISP: {isp}
                """,
                tooltip="Clique para ver detalhes"
            ).add_to(mapa)

            st.subheader("🌍 Origem do IP")

            st_folium(mapa,width=700,height=450)

    except:
        st.error("Erro na consulta")


# =========================
# RADAR GLOBAL
# =========================

st.header("🌎 Radar global de ameaças")

if mapa_ips:

    mapa_global=folium.Map(location=[0,0],zoom_start=2)

    for ip in mapa_ips:

        folium.CircleMarker(
            location=[ip["lat"],ip["lon"]],
            radius=6,
            color="red",
            fill=True,
            popup=f"""
            IP: {ip['ip']}<br>
            País: {ip['pais']}<br>
            ISP: {ip['isp']}
            """
        ).add_to(mapa_global)

    st_folium(mapa_global,width=900,height=500)


# =========================
# PHISHING
# =========================

st.header("🚨 Detector de Phishing")

msg=st.text_area("Cole mensagem ou link suspeito")

if st.button("Analisar mensagem"):

    palavras=[
        "pix","senha","urgente",
        "banco","login","clique",
        "transferência"
    ]

    score=0

    for p in palavras:

        if p in msg.lower():
            score+=1

    if score>=3:
        st.error("🚨 Alto risco de golpe")

    elif score>=1:
        st.warning("⚠️ Mensagem suspeita")

    else:
        st.success("🟢 Baixo risco")

    registrar("mensagem",score,msg[:100])


# =========================
# HISTÓRICO
# =========================

st.header("📊 Histórico SOC")

if historico:

    df=pd.DataFrame(historico)

    st.dataframe(df)


# =========================
# PAINEL SOC
# =========================

st.header("📡 Painel SOC")

eventos=len(historico)

suspeitos=len([e for e in historico if e.get("score",0)>=2])

alertas=suspeitos

c1,c2,c3=st.columns(3)

c1.metric("Eventos detectados",eventos)
c2.metric("Eventos suspeitos",suspeitos)
c3.metric("Alertas ativos",alertas)


# =========================
# RADAR
# =========================

st.header("🛰️ Radar de ameaça")

if alertas>=5:
    st.error("🚨 Nível alto de ameaça")

elif alertas>=1:
    st.warning("⚠️ Atividade suspeita")

else:
    st.success("🟢 Ambiente seguro")


# =========================
# RELATÓRIO
# =========================

st.header("📄 Gerar relatório")

if st.button("Gerar relatório PDF"):

    buffer=io.BytesIO()

    c=canvas.Canvas(buffer)

    y=800

    c.drawString(50,y,"Relatório Escudo Digital IA")

    y-=40

    for e in historico:

        linha=f"{e.get('data')} | {e.get('tipo')} | score:{e.get('score')}"

        c.drawString(50,y,linha)

        y-=20

    c.save()

    st.download_button(
        "Baixar relatório",
        buffer.getvalue(),
        "relatorio_soc.pdf"
    )
