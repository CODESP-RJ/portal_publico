import streamlit as st
import os

def local_css():
    st.markdown("""
    <style>
    .instruction-box {
        padding: 20px;
        background: #f0f2f6;
        border-radius: 10px;
        margin: 10px 0;
    }
    .file-card {
        padding: 15px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .module-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
    }
    .module-table td {
        padding: 8px;
        border-bottom: 1px solid #ddd;
    }
    .warning {
        color: #d6336c;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)


local_css()

with st.container():
    st.header("📌 INSTRUÇÕES GERAIS", divider="blue")
    with st.expander("sobre as tabelas auxiliares", expanded=True):
        st.markdown(
            """
            <div class="instruction-box">
                <p>As tabelas auxiliares são utilizadas para auxiliar o preenchimento dos arquivos modelo. Elas servem como referência para os campos obrigatórios e formatos esperados.</p>
                <p>Certifique-se de que os arquivos estejam no formato correto antes de realizar a importação.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

st.title("ℹ️ TABELAS AUXILIARES")

st.header("⬇️ Download de Modelos", divider="green")
st.info("Clique no botão correspondente para baixar o modelo desejado")

files_dir = "download/tabelas_auxiliares"
try:
    files = os.listdir(files_dir)

    categories = {
        'SIGMA': ['SERVICOS', 'MATERIAIS'],
        'TIPOS': ['TABELA_TIPOS_DE_BENS', 'TABELA_TIPOS_DE_DOCUMENTOS'],
        'TABELAS': ['TABELA_DESPESAS', 'TABELA_DE_RUBRICAS'],
    }

    for category, patterns in categories.items():
        with st.expander(f"📂 {category}", expanded=True):
            cols = st.columns(3)
            col_idx = 0
            for file in files:
                if any(p in file for p in patterns):
                    with cols[col_idx % 3]:
                        with open(os.path.join(files_dir, file), "rb") as fp:
                            st.download_button(
                                label=f"📄 {file.split('.')[0].replace('_', ' ').title()}",
                                data=fp,
                                file_name=file,
                                mime="text/csv",
                                use_container_width=True
                            )
                            col_idx += 1

except Exception as e:
    st.error(f"🚨 Erro ao carregar arquivos: {str(e)}")

st.divider()

with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("images/CGM_SAUDE.png", width=600, use_column_width=True)