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
            "VALIDADOR DE ARQUIVOS": [
                st.Page("web/routes/valida_arquivos/valida_insercao.py", title="Arquivos para Inserção de Dados"),
                st.Page("web/routes/valida_arquivos/valida_alteracao.py", title="Arquivos para Alteração e Exclusão de Dados"),
            ],
            "ARQUIVOS MODELO": [
                st.Page("web/routes/modelos/modelos_insercao.py", title="Arquivos para Inserção de Dados"),
                st.Page("web/routes/modelos/modelos_alteracao-exclusao.py", title="Arquivos para Alteração e Exclusão de Dados"),
            ],
            "CATÁLOGOS DE TABELAS": [
                st.Page("web/routes/tabelas_auxiliares/tabelas.py", title="Tabelas Auxiliares"),
            ],
            "TREINAMENTOS": [
                st.Page("web/routes/treinamentos/videos_explicativos.py", title="Vídeos Explicativos"),
            ],
            "SOBRE": [
                st.Page("web/routes/sobre/sobre.py", title="Sobre a Ferramenta"),
            ]
        }

        st.markdown("""
        <style>
            /* Estilos para navegação */
            [data-testid="stSidebarNav"] header.st-emotion-cache-1xlgjx2 {
                font-size: 15px !important;
                font-weight: 800 !important;
                border-left: 10px solid #004a8d !important;
                padding: 12px 16px !important;
                margin: 5px 0 !important;
            }

            /* Esconde o botão "View more" */
            [data-testid="stSidebarNav"] button:has(div p) {
                display: none !important;
            }

            /* Remove a barra de rolagem se não for necessária */
            [data-testid="stSidebarNav"] [data-testid="stSidebarNavItems"] {
                max-height: none !important;
                overflow: hidden !important;
            }

            /* Ajusta o espaçamento entre os itens */
            [data-testid="stSidebarNav"] [data-testid="stSidebarNavItems"] > div {
                padding: 8px 0 !important;
            }

            /* Remove a linha separadora (se houver) */
            [data-testid="stSidebarNav"] hr {
                display: none !important;
            }
        </style>
        """, unsafe_allow_html=True)

        st.logo(image="images/RIOPREFEITURA_Controladoria_Geral_horizontal_azul.png")
        pg = st.navigation(pages_app)
        pg.run()

    except Exception as e:
        handle_exception(type(e), e, e.__traceback__)

if __name__ == "__main__":
    main()