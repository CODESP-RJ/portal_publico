import streamlit as st
from urllib.parse import urlparse

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
    st.markdown('<div><h1>📚 Módulos de Treinamento</h1></div>', unsafe_allow_html=True)

    videos = {
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

    cols = st.columns(2)
    col_idx = 0
    for title, url in videos.items():
        with cols[col_idx]:
            st.markdown(f'<div class="section-title"><h4>{title}</h4></div>', unsafe_allow_html=True)
            st.video(url)
            col_idx = (col_idx + 1) % 2

st.markdown("---")
with st.container():
    st.markdown('<div><h1>🎥 Lives de Treinamento</h1></div>', unsafe_allow_html=True)

    live_videos = {
        "PARTE 1": "https://www.youtube.com/watch?v=6I0UbwRrp3M",
        "PARTE 2": "https://youtu.be/U1h0fmWYNnc"
    }

    cols = st.columns(2)
    col_idx = 0
    for title, url in live_videos.items():
        with cols[col_idx]:
            st.markdown(f'<div class="section-title"><h4>{title}</h4></div>', unsafe_allow_html=True)
            st.video(url)
            col_idx = (col_idx + 1) % 2

    st.info("Confira nossas gravações de treinamentos ao vivo realizados anteriormente")

st.divider()

with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("images/CGM_SAUDE.png", width=600, use_column_width=True)