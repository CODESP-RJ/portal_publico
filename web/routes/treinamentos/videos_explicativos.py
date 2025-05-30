import streamlit as st
from urllib.parse import urlparse
from utils.utils import footer

def local_css():
    st.markdown("""
    <style>
    .video-card {
        padding: 20px;
        background: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 15px 0;
        transition: transform 0.2s;
    }
    .video-card:hover {
        transform: translateY(-2px);
    }
    .section-title {
        color: #2c3e50;
        border-left: 5px solid #3498db;
        padding-left: 15px;
        margin: 25px 0;
    }
    .video-title {
        color: #2980b9;
        font-size: 1.1em;
        margin-bottom: 10px;
    }
    .category-box {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)


local_css()

with st.container():

    videos_ferramenta = {
        "01 Ferramenta de Validação de Arquivos": "https://www.youtube.com/watch?v=EFbB9zHx0Y8"
    }

    videos_conceitos = {
        "01 Introdução": "https://www.youtube.com/watch?v=R7dHPHMr4U0",
        "02 Módulo de Saldos": "https://www.youtube.com/watch?v=6Jlw00YKSqE",
        "03 Módulo de Receitas": "https://www.youtube.com/watch?v=vqcSG_cJIGc&t=6s",
        "04 Módulo de Despesas": "https://www.youtube.com/watch?v=FnMN3qnTSnQ&t=2s",
        "05 Módulo de Itens de Nota Fiscal": "https://www.youtube.com/watch?v=PDyAyPlp9OQ",
        "06 Módulo de Contratos de Terceiros": "https://www.youtube.com/watch?v=i0AzRaSjIWg",
        "07 Módulo de Fornecedores": "https://www.youtube.com/watch?v=6I0UbwRrp3M",
        "08 Módulo de Bens Patrimoniados": "https://www.youtube.com/watch?v=F1rBiB0qMn0&t=8s",
        "09 Entrega Negativa Bens Patrimoniados": "https://www.youtube.com/watch?v=dgspl05EYO4",
    }

    videos_anexos = {
        "01 Anexo I": "https://www.youtube.com/watch?v=-lhXeZMD6mM",
        "02 Anexo II": "https://www.youtube.com/watch?v=u-EPrMBlms0",
        "03 Anexo III": "https://www.youtube.com/watch?v=LmtUrJiXtow",
        "04 Anexo IV": "https://www.youtube.com/watch?v=FSiKSf-hhIE",
        "05 Anexos V e V 1": "https://www.youtube.com/watch?v=9BCWlNxXR24",
        "06 Anexo VII 1": "https://www.youtube.com/watch?v=fmpv05NRmas",
        "07 Anexo VII 2": "https://www.youtube.com/watch?v=3FJIJU36gS8"
    }

    videos_importacao = {
        "01 Informações necessárias para Importação": "https://www.youtube.com/watch?v=ljUUZ_V-noA",
        "02 Importação Módulo de Saldos": "https://www.youtube.com/watch?v=aK9O-oiPQyI",
        "03 Importação Módulo de Receitas": "https://www.youtube.com/watch?v=fL5qO_QPLBk",
        "04 Importação Módulo de Despesas": "https://www.youtube.com/watch?v=Mce1RNBUAX0",
        "05 Importação Módulo de Itens de Nota Fiscal": "https://www.youtube.com/watch?v=5FF1ypj5CZw",
        "06 Importação Módulo de Contratos de Terceiros": "https://www.youtube.com/watch?v=IFhSJGGThJo",
        "07 Importação Módulo de Bens Patrimoniados": "https://www.youtube.com/watch?v=TFjLZvsrEmI",
    }

    st.markdown('<div><h1>📚 Módulos de Treinamento</h1></div>', unsafe_allow_html=True)
    st.divider()

    st.markdown('<div><h2>📌Ferramenta</h2></div>', unsafe_allow_html=True)

    cols3 = st.columns(2)
    col_idx = 0
    for title, url in videos_ferramenta.items():
        with cols3[col_idx]:
            st.markdown(f'<div class="section-title"><h4>{title}</h4></div>', unsafe_allow_html=True)
            st.video(url)
            col_idx = (col_idx + 1) % 2

    st.divider()

    st.markdown('<div><h2>📌Conceitos</h2></div>', unsafe_allow_html=True)

    cols = st.columns(2)
    col_idx = 0
    for title, url in videos_conceitos.items():
        with cols[col_idx]:
            st.markdown(f'<div class="section-title"><h4>{title}</h4></div>', unsafe_allow_html=True)
            st.video(url)
            col_idx = (col_idx + 1) % 2

    st.divider()
    st.markdown('<div><h2>📌Importação</h2></div>', unsafe_allow_html=True)

    cols2 = st.columns(2)
    col_idx2 = 0
    for title, url in videos_importacao.items():
        with cols2[col_idx2]:
            st.markdown(f'<div class="section-title"><h4>{title}</h4></div>', unsafe_allow_html=True)
            st.video(url)
            col_idx2 = (col_idx2 + 1) % 2

    st.divider()

    st.markdown('<div><h2>📌Anexos</h2></div>', unsafe_allow_html=True)

    cols4 = st.columns(2)
    col_idx4 = 0
    for title, url in videos_anexos.items():
        with cols4[col_idx4]:
            st.markdown(f'<div class="section-title"><h4>{title}</h4></div>', unsafe_allow_html=True)
            st.video(url)
            col_idx4 = (col_idx4 + 1) % 2

st.markdown("---")
with st.container():
    st.markdown('<div><h1>🎥 Lives de Treinamento - OSINFO</h1></div>', unsafe_allow_html=True)

    live_videos = {
        "PRESTAÇÃO DE CONTAS PARTE 1": "https://www.youtube.com/watch?v=-TAIM3S6EzA",
        "PRESTAÇÃO DE CONTAS PARTE 2": "https://www.youtube.com/watch?v=U1h0fmWYNnc",
        "DESBLOQUEIO": "https://www.youtube.com/watch?v=NkDSlh8DzV0?si=ykEkyrIld0aPiYlI",
    }

    cols = st.columns(2)
    col_idx = 0
    for title, url in live_videos.items():
        with cols[col_idx]:
            st.markdown(f'<div class="section-title"><h4>{title}</h4></div>', unsafe_allow_html=True)
            st.video(url)
            col_idx = (col_idx + 1) % 2

    st.info("Confira nossas gravações de treinamentos ao vivo realizados anteriormente")

footer()