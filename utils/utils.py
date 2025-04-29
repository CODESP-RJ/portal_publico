import pyautogui
import requests
import json
import streamlit as st
from datetime import datetime
import random
import string
import requests
import streamlit as st
import pandas as pd
from datetime import datetime
from charset_normalizer import from_bytes

def reset_session_state_and_rerun(exclude_keys=None):
    if exclude_keys is None:
        exclude_keys = []
    for key in list(st.session_state.keys()):
        if key not in exclude_keys:
            del st.session_state[key]
    pyautogui.hotkey("ctrl","F5")
    #st.rerun(scope="app")

def exibir_resultados(df):
    st.divider()
    st.markdown("<h3 style='text-align: center;'>RESULTADO DA VALIDAÇÃO</h3>", unsafe_allow_html=True)
    st.dataframe(df.style.applymap(color_rows, subset=['VALIDACAO']))

def color_rows(val):
    color = 'green' if val == 'OK' else 'yellow' if 'Aviso' in val else 'red'
    return f'color: {color}'

def oferecer_download(df):
    csv = df.to_csv(index=False, sep=';').encode('utf-8')
    filename = f"validado_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    st.download_button(
        label="Baixar arquivo",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )

erros = {
    "01": "Todos os campos devem ser preenchidos!",
    "02": "O arquivo NÃO está no formato UTF-8!",
    "03": "O arquivo não tem o layout de Despesas ou não é compatível com o modelo DESPESAS GNOSIS.",
    "04": "O arquivo não tem o layout de Contratos de Terceiros ou não é compatível com o modelo ANEXOS.",
    "05": 'O arquivo não tem o layout de Contratos de Saldos ou não é compatível com o modelo SALDO IPCEP.',
    "06": 'O arquivo não tem o layout de Bens Patrimoniados ou não é compatível com o modelo BENS CEP28.'
}

def obter_instituicoes():
    with open("data/getOSUnitsListBySecretary.json", encoding='utf-8') as arqInstituicoes:
        resposta = json.load(arqInstituicoes)
        return [item.get('unidade_fantasia', 'Instituição não disponível') for item in resposta]

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

def obter_contas_bancarias():
    with open("data/osinfo.conta_bancaria.json", encoding='utf-8') as arqContasBancarias:
        resposta = json.load(arqContasBancarias)
        return resposta["rows"]

def obter_contratos():
    with open("data/getContractsList.json", encoding='utf-8') as arqContratos:
        resposta = json.load(arqContratos)
        return [item.get('num_contrato', 'Contrato não disponível') for item in resposta]

def criar_dicionario_instituicoes(nomes_instituicoes):
    return {nome: codigo for codigo, nome in (item.split(' - ', 1) for item in nomes_instituicoes if ' - ' in item)}

def carrega_secretarias():
    with open('./data/secretarias.json', encoding='utf-8') as arqSecretaria:
        dadosSecretarias = json.load(arqSecretaria)
    opcoes = []

    for secretaria in dadosSecretarias["secretarias"]:
        opcoes.append(secretaria["nome_secretaria"])

    return opcoes

def carrega_instituicoes():
    with open("data/instituicoes.json", encoding='utf-8') as arqInstituicoes:
        dadosInstituicoes = json.load(arqInstituicoes)
    opcoes = []

    for instituicao in dadosInstituicoes["VW_OS"]:
        opcoes.append(instituicao["DSC_OS"])

    return opcoes

def carrega_contratos():
    with open("data/contratos.json", encoding='utf-8') as arqContratos:
        dadosContratos = json.load(arqContratos)
    opcoes = []

    for contrato in dadosContratos["VW_CONTRATO_V2"]:
        opcoes.append(contrato["DSC_CONTRATO"])

    opcoes.sort()
    return opcoes

def carrega_instrumentos():
    with open("data/contratos.json", encoding='utf-8') as arqContratos:
        dadosContratos = json.load(arqContratos)

    return dadosContratos

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

        st.dataframe(df, use_container_width=True)

        st.divider()

        st.session_state.validar = True

        return df

    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None