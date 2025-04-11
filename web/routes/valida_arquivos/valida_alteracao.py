import streamlit as st
from utils import utils as util
from models.modulos import Modulos
from io import StringIO
import pandas as pd
import datetime
from web.components.instrucoes import instrucoes_validar_alteracoes

st.markdown("<h1 style='text-align: center;'>Valida arquivos de Alteração</h1>",
            unsafe_allow_html=True)

secretarias = util.obter_instituicoes()
instituicoes = util.carrega_instituicoes()
contratos = util.carrega_contratos()
validou = False

with st.form('Valida Importação', clear_on_submit=False):
    instituicaoEscolhida = st.selectbox('Instituição', instituicoes, index=None, placeholder="Selecione a Instituição")
    arquivo = st.file_uploader("Arquivo da ser verificado", type=['csv', 'xls', 'xlsx'], help="Envie um arquivo de cada vez")
    processou = st.form_submit_button("Processar")

    if processou:
        if instituicaoEscolhida and arquivo:
            with st.spinner('Processando...'):
                cod_os = instituicaoEscolhida.split(" ")[0]
                if arquivo.name.endswith('.xlsx') or arquivo.name.endswith('.xls') or arquivo.name.endswith('.XLS') or arquivo.name.endswith('.XLSX'):
                    df = pd.read_excel(arquivo)
                else:
                    string_data = StringIO(arquivo.getvalue().decode("utf-8-sig"))
                    df = pd.read_csv(string_data, sep=';', header=0, index_col=False, dtype=str)
                    df.columns = df.columns.str.upper().str.strip()
                    string_data.close()

                if 'ATRIBUTO' in df.columns and 'NOVO_VALOR' in df.columns:
                    df = df.dropna(how='all')
                    st.write("Prévia do arquivo original: ")
                    st.dataframe(df)
                    
                    modelos = Modulos()
                    df_filtrado = df[df["ATRIBUTO"].str.lower().isin([x.lower() for x in modelos.documentosPDF])]
                    if not df_filtrado.empty:
                        validou = True
                        st.write("Arquivo processado:")
                        st.dataframe(df_filtrado)
                        st.success('Processamento concluído!')
                    else:
                        st.error('O arquivo não tem imagens a serem alteradas!')
                else:
                    st.error('O arquivo não tem as colunas necessárias ("ATRIBUTO" e "NOVO_VALOR")!')
        else:
            st.error('Todos os campos devem ser preenchidos!')

if validou:
    nomeArquivo = f"VALIDADO_{cod_os[0]}_{datetime.datetime.now().strftime('%d-%m-%Y-%H-%M')}.csv"
    st.download_button(label="Download do arquivo CSV", data=df_filtrado.to_csv(sep=';', index=False), mime='text/csv', file_name=nomeArquivo)
    arquivo.close()

instrucoes_validar_alteracoes()