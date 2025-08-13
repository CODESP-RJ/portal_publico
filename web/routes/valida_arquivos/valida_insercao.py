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
from models.funcionarios import funcionarios_insercao_validador
from models.vinculos_de_trabalho import vinculos_de_trabalho_insercao_validador
from models.folha_de_pagamento import folha_de_pagamento_insercao_validador
from models.provisionamento import provisionamento_insercao_validador
from models.desligamento_em_lote import desligamento_em_lote_insercao_validador
from models.registry import RegistryValidators
from io import StringIO
from utils.utils import footer

st.markdown("<h1 style='text-align: center;'>Valida arquivos de Inserção</h1>", unsafe_allow_html=True)
st.divider()

tipo_arquivo = ['Despesas', 'Contratos de Terceiros', 'Saldos', 'Bens Patrimoniados', 'Itens de Nota Fiscal', 'Receitas', 'Fornecedores', 'Folha de Pagamento', 'Provisionamento', 'Desligamento em Lote', 'Funcionarios', 'Vínculos de Trabalho']

tipo_arquivo_modelo = {
    'Despesas': 'DESPESAS GNOSIS',
    'Contratos de Terceiros': 'MODELO ANEXO',
    'Saldos': 'SALDO IPCEP',
    'Bens Patrimoniados': 'BENS CEP28',
    'Itens de Nota Fiscal': 'ITENS DE NOTA FISCAL',
    'Receitas': 'IPCEP',
    'Fornecedores': 'FORNECEDOR GNOSIS',
    'Folha de Pagamento': 'MODELO FOLHA DE PAGAMENTO RH EXEMPLO',
    'Provisionamento': 'PROVISIONAMENTO RH EXEMPLO',
    'Desligamento em Lote': 'MODELO DESLIGAMENTO EM LOTE RH EXEMPLO',
    'Funcionarios': 'MODELO FUNCIONARIOS RH EXEMPLO',
    'Vínculos de Trabalho': 'MODELO VINCULO DE TRABALHO RH EXEMPLO'
}

tipo_arquivo_mapping = {
    'Despesas': 'modulo_despesas',
    'Contratos de Terceiros': 'modulo_contratos_de_terceiros',
    'Saldos': 'modulo_saldos',
    'Bens Patrimoniados': 'modulo_bens_patrimoniados',
    'Itens de Nota Fiscal': 'modulo_itens_nota_fiscal',
    'Receitas': 'modulo_receitas',
    'Fornecedores': 'modulo_fornecedores',
    'Folha de Pagamento': 'modulo_folha_de_pagamento',
    'Provisionamento': 'modulo_provisionamento',
    'Desligamento em Lote': 'modulo_desligamento_em_lote',
    'Funcionarios': 'modulo_funcionarios',
    'Vínculos de Trabalho': 'modulo_vinculos'
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
                # Obter lista de módulos válidos para inserção
                modulos_validos_ins = list(RegistryValidators._validators_ins.keys())
                modulos_validos_ins.sort()
                
                st.error(f"❌ **Tipo de arquivo não suportado:** {selected_type}")
                st.info(f"📋 **Tipos de arquivo válidos disponíveis:** {', '.join(tipo_arquivo)}")
                st.warning("Selecione um tipo de arquivo válido para continuar com a validação.")
                return

            selected_module = tipo_arquivo_mapping[selected_type]
            validator_class = RegistryValidators.get_validator_ins(selected_module)

            if not validator_class:
                # Obter lista de módulos válidos para inserção
                modulos_validos_ins = list(RegistryValidators._validators_ins.keys())
                modulos_validos_ins.sort()
                
                st.error(f"❌ **Validador não encontrado para:** {selected_type}")
                st.info(f"📋 **Módulos válidos disponíveis:** {', '.join(modulos_validos_ins)}")
                st.warning("O validador para este tipo de arquivo não está disponível.")
                return

            validator = validator_class(df)
            validator.configurar_modulo(selected_module)

            validator.validar_tudo()
            resultados = validator.obter_resultados()
            total_rows = len(df)
            processed_rows = 0
            error_rows = 0

            if not resultados.empty:
                exibir_resultados(resultados)
                ok_count = (resultados['VALIDACAO'] == "OK").sum()
                processed_rows += ok_count
                error_count = len(resultados) - ok_count
                error_rows += error_count
                if (resultados['VALIDACAO'] == 'OK').all():
                    st.success("Validação concluída e sem erros encontrados.")
                    st.toast("Todos os registros estão válidos!", icon="✅")
                    st.balloons()
                else:
                    st.error("Validação concluída, e com erros encontrados.")
                    st.toast("Alguns registros possuem erros!", icon="⚠️")

                oferecer_download(resultados)

                st.divider()
                st.subheader("Relatório de Processamento")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total de Registros", total_rows)
                col2.metric("Registros Válidos", processed_rows)
                col3.metric("Registros com Problemas", error_rows)

            else:
                st.toast("Nenhum registro válido encontrado no arquivo.", icon="⚠️")

        except Exception as e:
            st.error(f"Erro na validação: {str(e)}")
main()
instrucoes_validar_insercao()

footer()