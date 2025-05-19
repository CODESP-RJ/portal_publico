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
    with st.expander("requisitos de formatação", expanded=True):
        st.markdown("""
        <div class="instruction-box">
            <strong>Formatação obrigatória dos arquivos:</strong><br>
            🟢 Codificação: UTF-8<br>
            🟢 Formato: .csv ou .txt<br>
            🟢 Separador: ponto e vírgula <strong>;</strong><br>
            🟢 Estrutura: Cabeçalho + Corpo<br>
            🟢 Cabeçalho na 1ª linha (sem acentos/espaços)<br>
            🟢 Dados a partir da 2ª linha<br>
            🟢 Decimais com vírgula (ex: 1.234,56)<br>
            🟡 Separador de milhares opcional (usar ponto)
        </div>
        """, unsafe_allow_html=True)

with st.container():
    st.header("🔍 MODELOS NO OSINFO POR MODULO", divider="orange")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📑 Documentos Financeiros")
        st.markdown("""
        - **Saldos**: SALDO IPCEP
        - **Receitas**: IPCEP
        - **Despesas**: DESPESAS GNOSIS
        - **Itens de Nota Fiscal**: ITENS DE NOTA FISCAL
        """)

    with col2:
        st.subheader("📦 Cadastros Gerais")
        st.markdown("""
        - **Fornecedores**: FORNECEDOR GNOSIS
        - **Contratos de Terceiros**: MODELO ANEXO
        - **Bens Patrimoniados**: BENS CEP28
        """)

    st.markdown("""
    <div class="warning">
        ⚠️ CASO A INSTITUIÇÃO PARCEIRA ESTEJA INSERINDO DOCUMENTO OU ANEXO COMPLEMENTAR A PRESTAÇÃO DE CONTAS, DEVE SEGUIR AS ORIENTAÇÕES: 
        <a href="https://fazenda.prefeitura.rio/nmpc/" target="_blank">Ofício Circular CVL/SUBEX 005/2019</a>
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.title("📥 MODELOS DE INSERÇÃO")
st.header("⬇️ Download dos Arquivos Modelo", divider="green")
st.info("Clique no botão correspondente para baixar o modelo desejado")

files_dir = "download/modelos_insercao"
try:
    files = os.listdir(files_dir)

    categories = {
        'Financeiros': ['SALDOS_INSERCAO', 'RECEITAS_INSERCAO', 'DESPESAS_INSERCAO'],
        'Cadastros': ['FORNECEDORES_INSERCAO', 'CONTRATOS_DE_TERCEIROS_INSERCAO', 'BENS_PATRIMONIADOS_INSERCAO'],
        'Notas Fiscal': ['ITENS_DE_NOTA_FISCAL_INSERCAO'],
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

st.header("⬇️ Download das Instruções de Preenchimento", divider="red")
files_dir_imp = "download/instrucoes_preenchimento"
try:
    files_imp = os.listdir(files_dir_imp)

    categories = {
        'Tudo em um': ['INSTRUÇÕES PARA IMPORTAÇÃO COMPLETO'],
        'Por módulo': [
            'INSTRUÇÕES BASICAS DE FORMATAÇÃO DOS ARQUIVOS',
            'INSTRUÇÕES PARA IMPORTAÇÃO DE DESPESAS',
            'INSTRUÇÕES PARA IMPORTAÇÃO DE RECEITAS',
            'INSTRUÇÕES PARA IMPORTAÇÃO DE SALDOS',
            'INSTRUÇÕES PARA IMPORTAÇÃO DE FORNECEDORES',
            'INSTRUÇÕES PARA IMPORTAÇÃO DE CONTRATOS DE TERCEIROS',
            'INSTRUÇÕES PARA IMPORTAÇÃO DE BENS PATRIMONIADOSL',
            'INSTRUÇÕES PARA IMPORTAÇÃO DE ITENS DE NOTA FISCAL'

        ],
    }

    for category, patterns in categories.items():
        with st.expander(f"📂 {category}", expanded=True):
            cols = st.columns(3)
            col_idx = 0
            for file in files_imp:
                if any(p in file for p in patterns):
                    with cols[col_idx % 3]:
                        with open(os.path.join(files_dir_imp, file), "rb") as fp:
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