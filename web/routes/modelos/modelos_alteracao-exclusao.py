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
        font-size: 1.1em;
    }
    </style>
    """, unsafe_allow_html=True)


local_css()

with st.container():
    st.header("📌 INSTRUÇÕES GERAIS", divider="blue")
    with st.expander("requisitos de formatação", expanded=True):
        st.markdown("""
        <div class="instruction-box">
            <strong>Formatação obrigatória dos arquivos:</strong><br>
            🟢 Codificação: UTF-8<br>
            🟢 Formato: .csv<br>
            🟢 Separador: ponto e vírgula <strong>;</strong><br>
            🟢 Decimais com vírgula (ex: 1.234,56)<br>
            🟡 Separador de milhares opcional (usar ponto)
        </div>
        """, unsafe_allow_html=True)

with st.container():
    st.title("✏️ MODELOS DE ALTERAÇÃO")
    st.markdown("""
    <div class="warning">
        ⚠️ ATENÇÃO: O nome do ATRIBUTO deve corresponder ao módulo escolhido. 
    </div>
    """, unsafe_allow_html=True)

st.header("⬇️ Download dos Arquivos Modelo", divider="green")
st.info("Clique no botão correspondente para baixar o modelo desejado")

files_dir_alt = "download/modelos_alteracao"
files_dir_exc = "download/modelos_exclusao"
files_exc = os.listdir(files_dir_exc)
files_alt = os.listdir(files_dir_alt)

try:
    categories_alt = {
        'Financeiros': ['SALDOS_ALTERACAO', 'RECEITAS_ALTERACAO', 'DESPESAS_ALTERACAO'],
        'Cadastros': ['CONTRATOS_DE_TERCEIROS_ALTERACAO', 'BENS_PATRIMONIADOS_ALTERACAO'],
        'Notas Fiscal': ['ITENS_DE_NOTA_FISCAL_ALTERACAO'],
    }

    for category, patterns in categories_alt.items():
        with st.expander(f"📂 {category}", expanded=True):
            cols = st.columns(3)
            col_idx = 0
            for file in files_alt:
                if any(p in file for p in patterns):
                    with cols[col_idx % 3]:
                        with open(os.path.join(files_dir_alt, file), "rb") as fp:
                            st.download_button(
                                label=f"📄 {file.split('.')[0].replace('_', ' ').title()}",
                                data=fp,
                                file_name=file,
                                mime="text/csv",
                                use_container_width=True,
                                key=f"alt_{file}"
                            )
                            col_idx += 1

    st.divider()
    st.title("🗑️ MODELOS DE EXCLUSÃO")
    st.header("⬇️ Download dos Arquivos Modelo", divider="green")
    st.info("Clique no botão correspondente para baixar o modelo desejado")

    categories_exc = {
        'Financeiros': ['SALDOS_EXCLUSAO', 'RECEITAS_EXCLUSAO', 'DESPESAS_EXCLUSAO'],
        'Cadastros': ['CONTRATOS_DE_TERCEIROS_EXCLUSAO', 'BENS_PATRIMONIADOS_EXCLUSAO'],
        'Notas Fiscal': ['ITENS_DE_NOTA_FISCAL_EXCLUSAO'],
    }

    for category, patterns in categories_exc.items():
        with st.expander(f"📂 {category}", expanded=True):
            cols = st.columns(3)
            col_idx = 0
            for file in files_exc:
                if any(p in file for p in patterns):
                    with cols[col_idx % 3]:
                        with open(os.path.join(files_dir_exc, file), "rb") as fp:
                            st.download_button(
                                label=f"📄 {file.split('.')[0].replace('_', ' ').title()}",
                                data=fp,
                                file_name=file,
                                mime="text/csv",
                                use_container_width=True,
                                key=f"exc_{file}"
                            )
                            col_idx += 1

except Exception as e:
    st.error(f"🚨 Erro ao carregar arquivos: {str(e)}")

st.divider()

with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("images/CGM_SAUDE.png", width=600, use_column_width=True)