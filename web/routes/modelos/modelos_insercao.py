import streamlit as st
import os
from utils.utils import footer

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
    .drive-link-box {
        padding: 20px;
        background: #F7F7F7;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
        border: 2px solid #B0B0B0;
    }
    
    .drive-button {
        background-color: #8C8C8C;
        color: white;
        padding: 15px 30px;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        text-decoration: none;
        display: inline-block;
        margin: 10px;
        transition: background-color 0.3s;
    }

    .drive-button:hover {
        background-color: #5A5A5A;
        text-decoration: none;
        color: white;
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
    st.divider()
    st.markdown("""
    <div class="warning">
        CASO A INSTITUIÇÃO PARCEIRA ESTEJA INSERINDO DOCUMENTO OU ANEXO COMPLEMENTAR A PRESTAÇÃO DE CONTAS, DEVE SEGUIR AS ORIENTAÇÕES: 
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
        'Recursos Humanos': ['FUNCIONARIOS_INSERCAO', 'VINCULO_DE_TRABALHO_INSERCAO', 'FOLHA_DE_PAGAMENTO_INSERCAO', 'PROVISIONAMENTO_INSERCAO'],
        'Desligamento em Lote': ['DESLIGAMENTO_EM_LOTE']
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
                                width='content'
                            )
                            col_idx += 1
except Exception as e:
    st.error(f"🚨 Erro ao carregar arquivos: {str(e)}")

st.header("⬇️ Download das Instruções de Preenchimento", divider="red")

st.markdown("""
<div class="drive-link-box">
    <h4>📋 Instruções de Preenchimento</h4>
    <p>Acesse o Google Drive para baixar as instruções detalhadas de preenchimento dos modelos:</p>
    <a href="https://drive.google.com/drive/folders/1jW34NRzbY8QzQJ2AYopapS9S4Vlxus3n?usp=drive_link" 
       target="_blank" class="drive-button">
    📁 Acessar Instruções no Google Drive
    </a>
    <br>
    <small style="color: #666;">O link será aberto em uma nova aba</small>
</div>
""", unsafe_allow_html=True)

footer()