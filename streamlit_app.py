import streamlit as st
import logging
import sys
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_exception(exc_type, exc_value, exc_traceback):
    """Captura exceções não tratadas"""
    logging.critical(
        "Erro não tratado",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    st.error("Ocorreu um erro crítico. A página será recarregada.")
    st.session_state.clear()
    st.rerun()

sys.excepthook = handle_exception

def main():
    try:
        st.markdown("""<style> .big-font { font-size: 24px !important; font-weight: bold !important; } </style>""", unsafe_allow_html=True)
        pages_app = {
            "VALIDAR ARQUIVOS": [
                st.Page("web/routes/valida_arquivos/valida_importacao.py", title="Importações"),
                st.Page("web/routes/valida_arquivos/valida_alteracao.py", title="Alterações"),
            ],
            "MODELOS": [
                st.Page("web/routes/modelos/modelos_importacao.py", title="Arquivos de Importação"),
                st.Page("web/routes/modelos/modelos_alteracao.py", title="Arquivos de Alteração"),
                st.Page("web/routes/modelos/modelos_exclusao.py", title="Arquivos de Exclusão"),
            ],
            "TABELAS AUXILIARES": [
                st.Page("web/routes/tabelas_auxiliares/tabelas.py", title="Tabelas Auxiliares"),
            ],
            "TUTORIAIS": [
                st.Page("web/routes/tutoriais/videos_explicativos.py", title="Vídeos Explicativos"),
            ],
            "SOBRE": [
                st.Page("web/routes/sobre/sobre.py", title="Sobre a Ferramenta"),
            ]
        }
        st.logo(image="images/CGM_SAUDE.png")
        pg = st.navigation(pages_app)
        pg.run()

    except Exception as e:
        handle_exception(type(e), e, e.__traceback__)

if __name__ == "__main__":
    main()