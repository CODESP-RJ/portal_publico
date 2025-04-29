import streamlit as st
from io import StringIO
import pandas as pd
import datetime
from models.validators.base_validator import BaseValidator
from models.contratos_de_terceiros.contratos_terceiros_validator import ContratosTerceirosValidator
from models.despesas.despesas_validator import DespesasValidator
from models.saldos.saldos_validator import SaldosValidator
from models.bens_patrimoniados.bens_patrimoniados_validator import BensPatrimoniadosValidator
from models.itens_de_nota_fiscal.itens_de_nota_fiscal_validator import ItensDeNotaFiscalValidator
from models.receitas.receitas_validator import ReceitasValidator
from models.common import (
    LISTA_ATRIBUTOS_CONTRATOS_DE_TERCEIROS,
    LISTA_ATRIBUTOS_DESPESAS,
    LISTA_ATRIBUTOS_BENS_PATRIMONIADOS,
    LISTA_ATRIBUTOS_ITENS_DE_NOTA_FISCAL,
    LISTA_ATRIBUTOS_RECEITAS,
    LISTA_ATRIBUTOS_SALDOS
)
from web.components.instrucoes import instrucoes_validar_alteracoes_exclusoes
from utils.tratamentos import limpar_dados
from utils.utils import color_rows, exibir_resultados, oferecer_download

st.markdown("<h1 style='text-align: center;'>Valida arquivos de Alterações/Exclusões</h1>", unsafe_allow_html=True)

tipo_arquivo_options = [
    'Contratos de Terceiros',
    'Despesas',
    'Saldos',
    'Bens Patrimoniados',
    'Itens de Nota Fiscal',
    'Receitas'
]

def main():
    with st.form('main_form'):
        tipo_arquivo = st.selectbox('Tipo de Arquivo', tipo_arquivo_options, index=None, placeholder="Selecione o Tipo de Arquivo")
        tipo_acao = st.selectbox('Tipo de Ação', ['Alteração', 'Exclusão'], index=None, placeholder="Selecione o Tipo de Ação")
        arquivo = st.file_uploader("Arquivo CSV", type="csv")
        submitted = st.form_submit_button("Processar")

    if submitted:
        if not all([tipo_arquivo, tipo_acao, arquivo]):
            st.error("Preencha todos os campos!")
            return

        try:
            st.divider()
            st.markdown("<h3 style='text-align: center;'>EXIBIÇÃO DO ARQUIVO</h3>", unsafe_allow_html=True)
            df = processar_arquivo(arquivo)
            st.dataframe(df)

            validator_map = {
                'Contratos de Terceiros': ContratosTerceirosValidator,
                'Despesas': DespesasValidator,
                'Saldos': SaldosValidator,
                'Bens Patrimoniados': BensPatrimoniadosValidator,
                'Itens de Nota Fiscal': ItensDeNotaFiscalValidator,
                'Receitas': ReceitasValidator
            }

            if tipo_arquivo not in validator_map:
                st.error("Validador não implementado para este tipo de arquivo")
                return None

            validator_class = validator_map[tipo_arquivo]
            validator = validator_class(df, tipo_acao)
            try:
                validator.check_header()
                validator.check_ano_mes_ref()
            except Exception as e:
                st.error(f"Erro na validação 1: {str(e)}")
                st.stop()

            if tipo_acao == "Alteração":
                df = df[df['ACAO'] == 'ALTERACAO']
            elif tipo_acao == "Exclusão":
                df = df[df['ACAO'] == 'EXCLUSAO']
            df = df[df['TIPO_MODULO'] == tipo_arquivo.upper()]

            if (df.empty):
                st.warning("Nenhum registro encontrado neste arquivo para o tipo de módulo e ação selecionados.")
                return

            validado = processar_validacao(tipo_arquivo, df, tipo_acao, validator)

            if validado is not None:
                exibir_resultados(validado)
                st.info("Seu arquivo foi filtrado para o módulo e ação selecionados.")
                oferecer_download(validado)

        except Exception as e:
            st.error(f"Erro na validação 2: {str(e)}")


def processar_arquivo(arquivo):
    string_data = StringIO(arquivo.getvalue().decode("utf-8-sig"))
    df = pd.read_csv(string_data, sep=';', dtype=str)
    df.columns = df.columns.str.strip().str.upper()
    return limpar_dados(df)


def processar_validacao(tipo_arquivo, df, tipo_acao, validator):
    try:
        if tipo_acao != "Exclusão":
            validator.check_atributos()
            return validator.validate_data()
        return
    except Exception as e:
        st.error(f"Erro na validação 3: {str(e)}")
        st.stop()

main()
instrucoes_validar_alteracoes_exclusoes()