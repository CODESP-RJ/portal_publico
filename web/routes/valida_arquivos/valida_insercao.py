import streamlit as st
import pandas as pd
import datetime
from web.components.instrucoes import instrucoes_validar_insercao
from utils.tratamentos import limpar_dados
from utils.utils import color_rows, exibir_resultados, oferecer_download, processar_arquivo
from models.base_validador import BaseValidatorIns
from models.receitas import receitas_insercao_validador
from models.saldos import saldos_insercao_validador
from models.itens_de_nota_fiscal import itens_de_nota_fiscal_insercao_validador
from models.despesas import despesas_insercao_validador
from models.contratos_de_terceiros import contratos_de_terceiros_insercao_validador
from models.bens_patrimoniados import bens_patrimoniados_insercao_validador
from models.fornecedores import fornecedores_insercao_validador
from models.registry import RegistryValidators
from io import StringIO
from utils.utils import footer

st.markdown("<h1 style='text-align: center;'>Valida arquivos de Inserção</h1>", unsafe_allow_html=True)
st.divider()

tipo_arquivo = ['Despesas', 'Contratos de Terceiros', 'Saldos', 'Bens Patrimoniados', 'Itens de Nota Fiscal', 'Receitas', 'Fornecedores']
tipo_arquivo_modelo = {
    'Despesas': 'DESPESAS GNOSIS',
    'Contratos de Terceiros': 'MODELO ANEXO',
    'Saldos': 'SALDO IPCEP',
    'Bens Patrimoniados': 'BENS CEP28',
    'Itens de Nota Fiscal': 'ITENS DE NOTA FISCAL',
    'Receitas': 'IPCEP',
    'Fornecedores': 'FORNECEDOR GNOSIS'
}

tipo_arquivo_mapping = {
    'Despesas': 'modulo_despesas',
    'Contratos de Terceiros': 'modulo_contratos_de_terceiros',
    'Saldos': 'modulo_saldos',
    'Bens Patrimoniados': 'modulo_bens_patrimoniados',
    'Itens de Nota Fiscal': 'modulo_itens_nota_fiscal',
    'Receitas': 'modulo_receitas',
    'Fornecedores': 'modulo_fornecedores'
}

tipoarquivo_escolhido = st.selectbox(
    'Selecione o tipo de arquivo:',
    tipo_arquivo,
    index=None,
    placeholder="Selecione o Tipo de Arquivo",
    key='tipoarquivo_escolhido'
)

if st.session_state.tipoarquivo_escolhido:
    st.info(f"Modelo: {tipo_arquivo_modelo[st.session_state.tipoarquivo_escolhido]}")

def main():
    with st.form('main_form'):
        arquivo = st.file_uploader("Selecione ou arraste um arquivo CSV", type="csv")
        submitted = st.form_submit_button("Processar", use_container_width=True)

    if submitted:
        if not arquivo:
            st.error("Selecione um arquivo!")
            st.toast("Nenhum arquivo selecionado!", icon="⚠️")
            return

        try:
            st.divider()

            df = processar_arquivo(arquivo, 1)
            selected_type = st.session_state.tipoarquivo_escolhido

            if selected_type not in tipo_arquivo_mapping:
                st.error("Tipo de arquivo não suportado.")
                return

            selected_module = tipo_arquivo_mapping[selected_type]
            validator_class = RegistryValidators.get_validator_ins(selected_module)

            if not validator_class:
                st.error(f"Validador para {selected_type} não encontrado.")
                return

            validator = validator_class(df)
            validator.configurar_modulo(selected_module)

            validator.validar_tudo()
            resultados = validator.obter_resultados()

            if not resultados.empty:
                exibir_resultados(resultados)

                if (resultados['VALIDACAO'] == 'OK').all():
                    st.success("Validação concluída e sem erros encontrados.")
                    st.toast("Todos os registros estão válidos!", icon="✅")
                    st.balloons()
                else:
                    st.error("Validação concluída, e com erros encontrados.")
                    st.toast("Alguns registros possuem erros!", icon="⚠️")

                oferecer_download(resultados)
            else:
                st.warning("Nenhum registro válido encontrado no arquivo.")


        except Exception as e:
            st.error(f"Erro na validação: {str(e)}")
main()
instrucoes_validar_insercao()

footer()