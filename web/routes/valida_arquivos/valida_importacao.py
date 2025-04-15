import streamlit as st
from utils import utils as util
from io import StringIO
import pandas as pd
import datetime
from models.modelos_arquivos import Cabecalho
from models.despesas.despesas_df import DespesasDFImportacao
from models.contratos_de_terceiros.contratos_terceiros_df import ContratosTerceirosDFImportacao
from models.saldos.saldos_df import SaldosDFImportacao
from models.bens_patrimoniados.bens_patrimoniados_df import BensPatrimoniadosDFImportacao
from models.fornecedores.fornecedores_df import FornecedoresDFImportacao
from models.itens_de_nota_fiscal.itens_nota_fiscal_df import ItensNotaFiscalDFImportacao
from models.receitas.receitas_df import ReceitasDFImportacao
from web.components.instrucoes import instrucoes_validar_importacoes

st.markdown("<h1 style='text-align: center;'>Valida arquivos de Inserção</h1>",
            unsafe_allow_html=True)

tipo_arquivo = ['Despesas', 'Contratos de Terceiros', 'Saldos', 'Bens Patrimoniados', 'Itens de Nota Fiscal', 'Receitas', 'Fornecedores']

secretarias = util.obter_instituicoes()
instituicoes = util.carrega_instituicoes()
contratos = util.carrega_contratos()
validou = ""

def check_columns(columns):
    matched_columns = []
    for column in df.columns:
        if column in columns:
            matched_columns.append(column)
    return matched_columns

with st.form('Valida Inserção', clear_on_submit=False):
    tipoarquivo_escolhido = st.selectbox('Tipo de Arquivo', tipo_arquivo, index=None, placeholder="Selecione o Tipo de Arquivo")
    arquivo = st.file_uploader("Arquivo a ser verificado", type="csv", help="Envie um arquivo de cada vez")
    processou = st.form_submit_button("Processar")

    if processou:
        if arquivo and tipoarquivo_escolhido:
            pBar = st.progress(0)
            try:                        
                string_data = StringIO(arquivo.getvalue().decode("utf-8-sig"))
                cabecalho_arquivo = string_data.readline().strip()
                string_data.seek(0)
                
                cabecalho_arquivo = Cabecalho.trata_cabecalho(cabecalho_arquivo)

                df = pd.read_csv(string_data, sep=';', header=0, index_col=False, dtype=str)
                tamanho = len(df)                        
                st.info("Quantidade de linhas do arquivo: " +str(tamanho))
                st.write("Arquivo original:")
                st.dataframe(df)                        
                los = Cabecalho.get_os_list_type()
                df.columns = df.columns.str.strip().str.upper()
                listaOS = check_columns(los)
                if not len(listaOS) > 0:
                    raise Exception("Não foi possível identificar o código da instituição no arquivo enviado")
                if len(listaOS) > 0:
                    if tipoarquivo_escolhido == "Despesas":
                        despesas = DespesasDFImportacao(df, 'removerparam', listaOS, pBar, 'despesas', 'importacao')
                        despesas.check_header()
                        st.info('O cabeçalho é compatível com o modelo DESPESAS.')
                        if despesas.check_df_data():
                            validou = 1
                        st.dataframe(df)

                    elif tipoarquivo_escolhido == "Contratos de Terceiros":
                        contratos = ContratosTerceirosDFImportacao(df, 'removerparam', listaOS, pBar, 'contratos_terceiros', 'importacao')
                        contratos.check_header()
                        st.info('O cabeçalho é compatível com o modelo CONTRATOS DE TERCEIROS.')
                        if contratos.check_df_data():
                            validou = 1
                        st.dataframe(df)

                    elif tipoarquivo_escolhido == "Saldos":
                        saldos = SaldosDFImportacao(df, 'removerparam', listaOS, pBar, 'saldos', 'importacao')
                        saldos.check_header()
                        st.info('O cabeçalho é compatível com o modelo SALDOS.')
                        if saldos.check_df_data():
                            validou = 1
                        st.dataframe(df)

                    elif tipoarquivo_escolhido == "Bens Patrimoniados":
                        bens = BensPatrimoniadosDFImportacao(df, 'removerparam', listaOS, pBar, 'bens_patrimoniados', 'importacao')
                        bens.check_header()
                        st.info('O cabeçalho é compatível com o modelo BENS PATRIMONIADOS.')
                        if bens.check_df_data():
                            validou = 1
                        st.dataframe(df)

                    elif tipoarquivo_escolhido == "Fornecedores":
                        fornecedores = FornecedoresDFImportacao(df, 'removerparam', listaOS, pBar, 'fornecedores', 'importacao')
                        fornecedores.check_header()
                        st.info('O cabeçalho é compatível com o modelo FORNECEDORES.')
                        if fornecedores.check_df_data(tipoarquivo_escolhido):
                            validou = 1
                        st.dataframe(df)
                    
                    elif tipoarquivo_escolhido == "Itens de Nota Fiscal":
                        itens_nf = ItensNotaFiscalDFImportacao(df, 'removerparam', listaOS, pBar, 'itens_nota_fiscal', 'importacao')
                        itens_nf.check_header()
                        st.info('O cabeçalho é compatível com o modelo ITENS NOTA FISCAL.')
                        if itens_nf.check_df_data():
                            validou = 1
                        st.dataframe(df)

                    elif tipoarquivo_escolhido == "Receitas":
                        receitas = ReceitasDFImportacao(df, 'removerparam', listaOS, pBar, 'receitas', 'importacao')
                        receitas.check_header()
                        st.info('O cabeçalho é compatível com o modelo RECEITAS.')
                        if receitas.check_df_data():
                            validou = 1
                        st.dataframe(df)
                    else:
                        st.warning("Não foi possível identificar qual a verificação deve ser realizada.")
                    
                    filtroProblemas = df[df['PROBLEMAS'] != '' ]
                    if filtroProblemas.shape[0] > 0 :
                        st.warning(f"O arquivo possui {filtroProblemas.shape[0]} linhas com problemas")
                        st.warning(f"Verifique a coluna PROBLEMAS na planilha acima ou baixe o arquivo")
                    else:
                        st.success(f"Arquivo processado sem linhas com problemas")

            except UnicodeDecodeError:
                st.error(util.erros["02"])
            except Exception as e:
                st.error(f"Operação abortada: {e}")

        else:
            st.error('Todos os campos devem ser preenchidos!')

if validou:
    st.write("Arquivo processado:")
    st.dataframe(df)
    nomeArquivo = f"VALIDADO_{str(df.iloc[0,0])}_{datetime.datetime.now().strftime('%d-%m-%Y-%H-%M')}.csv"
    st.download_button(label="Download do arquivo CSV", data=df.to_csv(sep=';', index=False), mime='text/csv', file_name=nomeArquivo)

instrucoes_validar_importacoes()