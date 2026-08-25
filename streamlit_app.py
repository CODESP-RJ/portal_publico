import streamlit as st
import logging
import sys
from pathlib import Path
from supabase import create_client

# Adiciona o diretório raiz ao sys.path para permitir imports absolutos
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Importa componentes de seleção de usuário
from web.components.user_selection_modal import show_user_selection_modal, get_user_info_display
from utils.config import (
    has_google_credentials,
    has_supabase_credentials,
    is_development_environment,
)

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

@st.cache_resource
def init_connection():
    """
    Inicializa conexão com Supabase.
    Em development (ou com placeholders), retorna None em vez de derrubar a aplicação.
    """
    if not has_supabase_credentials():
        if is_development_environment():
            logger.info("Supabase não configurado. Modo development: conexão ignorada.")
            return None
        raise RuntimeError(
            "Credenciais do Supabase não configuradas. "
            "Copie .streamlit/secrets.toml.example para .streamlit/secrets.toml "
            "e preencha as chaves, ou use environment = \"development\"."
        )

    try:
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        if "SUPABASE_SERVICE_KEY" in st.secrets["connections"]["supabase"]:
            key = st.secrets["connections"]["supabase"]["SUPABASE_SERVICE_KEY"]
        else:
            key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        if is_development_environment():
            logger.warning("Falha ao conectar no Supabase em development: %s", e)
            return None
        raise

def main():
    try:
        # Verifica se o usuário já selecionou o tipo (Secretaria ou Instituição)
        # Se não, mostra o modal de seleção
        if is_development_environment() and (
            not has_supabase_credentials() or not has_google_credentials()
        ):
            st.sidebar.warning(
                "Modo development: logs (Supabase) e/ou validação no BigQuery "
                "estão indisponíveis. A validação local dos arquivos continua ativa."
            )

        if 'tipo_usuario' not in st.session_state or not st.session_state.tipo_usuario:
            try:
                supabase = init_connection()
                if not show_user_selection_modal(supabase):
                    # Se o usuário ainda não confirmou, não continua
                    return
            except Exception as e:
                # Se houver erro ao conectar com Supabase, permite continuar sem log
                st.warning("⚠️ Não foi possível conectar ao sistema de logs. A aplicação continuará funcionando normalmente.")
                if 'tipo_usuario' not in st.session_state:
                    st.session_state.tipo_usuario = "DESCONHECIDO"
        
        # Exibe informações do usuário no sidebar
        user_info = get_user_info_display()
        if user_info:
            with st.sidebar:
                st.info(user_info)
                if st.button("🔄 Alterar Identificação"):
                    st.session_state.pop('tipo_usuario', None)
                    st.session_state.pop('secretaria_selecionada', None)
                    st.session_state.pop('instituicao_selecionada', None)
                    st.rerun()
        
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
                st.Page("web/routes/treinamentos/videos.py", title="Vídeos"),
            ],
            "SOBRE": [
                st.Page("web/routes/sobre/sobre.py", title="Sobre a Ferramenta"),
            ]
        }

        st.markdown("""
        <style>
            /* Estilos para navegação */
            [data-testid="stSidebarNav"] header.st-emotion-cache-95klgh {
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