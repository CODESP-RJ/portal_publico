import requests
import json
import streamlit as st
import random
import string
import requests
import pandas as pd
from datetime import datetime
from charset_normalizer import from_bytes
from io import StringIO
from utils.tratamentos import limpar_dados

def footer():
    st.divider()

    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("images/RIOPREFEITURA_Controladoria_Geral_horizontal_azul.png")
            st.markdown(
                "<p style='text-align: center; font-size: 10px;'><strong>APOIO:</strong> SMS/SUBG/CTGOS</p>",
                unsafe_allow_html=True
            )

def processar_arquivo(arquivo, func=None):
    try:
        conteudo_decodificado = arquivo.getvalue().decode("utf-8-sig")
        string_data = StringIO(conteudo_decodificado)

        df = pd.read_csv(string_data, sep=';', dtype=str)
        df.columns = df.columns.str.strip().str.upper()

        return limpar_dados(df) if func is None else df

    except UnicodeDecodeError:
        st.error(erros["02"])
        st.stop()
        return None
    except Exception as e:
        st.error(f"Erro ao processar arquivo: {str(e)}")
        return None

def exibir_resultados(df):
    st.markdown("<h3 style='text-align: center;'>RESULTADO DA VALIDAÇÃO</h3>", unsafe_allow_html=True)

    if 'VALIDACAO' in df.columns:
        df['VALIDACAO'] = df['VALIDACAO'].astype(str)

    # Verifica quais colunas existem antes de aplicar o estilo
    subset_cols = []
    if 'VALIDACAO' in df.columns:
        subset_cols.append('VALIDACAO')
    if 'VALIDACAO_ADICIONAL' in df.columns:
        subset_cols.append('VALIDACAO_ADICIONAL')
    
    if subset_cols:
        styled_df = df.style.map(color_rows, subset=subset_cols) \
            .set_properties(**{'text-align': 'left'})
    else:
        styled_df = df.style.set_properties(**{'text-align': 'left'})

    st.dataframe(styled_df, width='content')

def color_rows(val):
    color = 'green' if val == 'OK' else 'yellow' if 'Aviso' in val else 'red'
    return f'color: {color}'

def oferecer_download(df):
    csv = df.to_csv(index=False, sep=';').encode('utf-8')
    filename = f"validado_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    col1, col2, col3 = st.columns(3)
    with col2:
        st.download_button(
            label="Baixar arquivo",
            data=csv,
            file_name=filename,
            mime='text/csv',
            width='content'
        )

erros = {
    "01": "Todos os campos devem ser preenchidos!",
    "02": "O arquivo NÃO está no formato UTF-8!",
    "03": "O arquivo não tem o layout de Despesas ou não é compatível com o modelo DESPESAS GNOSIS.",
    "04": "O arquivo não tem o layout de Contratos de Terceiros ou não é compatível com o modelo ANEXOS.",
    "05": 'O arquivo não tem o layout de Contratos de Saldos ou não é compatível com o modelo SALDO IPCEP.',
    "06": 'O arquivo não tem o layout de Bens Patrimoniados ou não é compatível com o modelo BENS CEP28.'
}

def obter_tipos_bens():
    with open("data/getAssetTypes.json", encoding='utf-8') as arqTiposBens:
        resposta = json.load(arqTiposBens)
        return resposta

def obter_tipos_rubricas():
    with open("data/getExpendituresList.json", encoding='utf-8') as arqTiposRubricas:
        resposta = json.load(arqTiposRubricas)
        return resposta

def obter_tipos_despesas():
    with open("data/getExpenseTypesList.json", encoding='utf-8') as arqTiposDespesas:
        resposta = json.load(arqTiposDespesas)
        return resposta

def obter_tipos_documentos():
    with open("data/getDocumentTypesList.json", encoding='utf-8') as arqTiposDocumentos:
        resposta = json.load(arqTiposDocumentos)
        return resposta

def obter_tipos_de_vinculo():
    with open("data/employmentRelationshipType.json", encoding='utf-8') as arqTiposVinculo:
        resposta = json.load(arqTiposVinculo)
        return resposta

def obter_contas_bancarias():
    with open("data/osinfo.conta_bancaria.json", encoding='utf-8') as arqContasBancarias:
        resposta = json.load(arqContasBancarias)
        return resposta["rows"]

def obter_contratos():
    with open("data/getContractsList.json", encoding='utf-8') as arqContratos:
        resposta = json.load(arqContratos)
        return [item.get('num_contrato', 'Contrato não disponível') for item in resposta]

def detectar_codificacao(arquivo):
    conteudo = arquivo.read()
    resultado = from_bytes(conteudo).best()
    arquivo.seek(0)
    return resultado.encoding if resultado else "latin1"

def upload_arquivo(arquivo):
    """
    Função para upload de arquivos CSV ou Excel.

    Permite ao usuário enviar um arquivo CSV ou Excel, que é então carregado
    e exibido como um DataFrame do pandas.

    Returns:
        DataFrame or None: O DataFrame com os dados do arquivo carregado ou None se nenhum arquivo foi carregado.
    """
    try:
        with st.spinner("Processando arquivo..."):
            if arquivo.name.endswith('.csv') or arquivo.name.endswith('.CSV'):
                codificacao = detectar_codificacao(arquivo)
                df = pd.read_csv(arquivo, sep=None, encoding=codificacao, engine='python')
                df.columns = df.columns.str.upper().str.strip()
            elif arquivo.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(arquivo)
            else:
                st.error("Tipo de arquivo não suportado.")
                return None

        df = df.dropna(how='all')
        df['ID'] = df['ID'].astype(int)

        cols = st.columns(2)
        with cols[0]:
            st.markdown(f''':blue[**Quantidade de linhas do arquivo:**] {len(df)}''')
        with cols[1]:
            st.markdown(f''':blue[**Quantidade de ID's do arquivo:**] {len(df['ID'].unique())}''')

        st.divider()
        st.markdown("<h2 style='text-align: center;'>Exibição do Arquivo</h2>", unsafe_allow_html=True)

        st.dataframe(df, width='content')

        st.divider()

        st.session_state.validar = True

        return df

    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None