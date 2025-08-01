import streamlit as st
from io import StringIO
import pandas as pd
import datetime
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
from utils.utils import color_rows, exibir_resultados, oferecer_download, processar_arquivo

from models.contratos_de_terceiros.contratos_terceiros_alteracao_validador import ContratosTerceirosValidator
from models.despesas.despesas_alteracao_validador import DespesasValidator
from models.saldos.saldos_alteracao_validator import SaldosValidator
from models.bens_patrimoniados.bens_patrimoniados_alteracao_validador import BensPatrimoniadosValidator
from models.itens_de_nota_fiscal.itens_de_nota_fiscal_alteracao_validador import ItensDeNotaFiscalValidator
from models.receitas.receitas_alteracao_validator import ReceitasValidator
from models.folha_de_pagamento.folha_de_pagamento_alteracao_validador import FolhaDePagamentoValidador
from models.provisionamento.provisionamento_alteracao_validador import ProvisionamentoValidador

from models.registry import RegistryValidators
from utils.utils import footer

st.markdown("<h1 style='text-align: center;'>Valida arquivos de Alterações/Exclusões</h1>", unsafe_allow_html=True)
st.divider()

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
            df = processar_arquivo(arquivo)

            if 'TIPO_MODULO' not in df.columns:
                st.error("O arquivo não contém a coluna 'TIPO_MODULO' necessária para a validação.")
                return

            if 'ACAO' not in df.columns:
                st.error("O arquivo não contém a coluna 'ACAO' necessária para a validação.")
                return

            resultados = []
            modulos_nao_reconhecidos = []
            acao_nao_reconhecida = []

            total_rows = len(df)
            processed_rows = 0
            error_rows = 0

            for modulo in df['TIPO_MODULO'].unique():
                modulo_normalizado = modulo.strip().upper()

                validator_class = RegistryValidators.get_validator_alt_exc(modulo)

                if validator_class is None:
                    modulos_nao_reconhecidos.append(modulo)
                    error_rows += 1
                    continue

                for acao in df['ACAO'].unique():
                    acao_normalizada = acao.strip().upper()

                    if acao_normalizada not in ['ALTERACAO', 'EXCLUSAO']:
                        acao_nao_reconhecida.append(acao)
                        error_rows += 1
                        continue

                    df_filtrado = df[
                        (df['TIPO_MODULO'].str.strip().str.upper() == modulo_normalizado) &
                        (df['ACAO'].str.strip().str.upper() == acao_normalizada)
                        ]

                    if df_filtrado.empty:
                        continue

                    validador = validator_class(df_filtrado,
                                                "Alteração" if acao_normalizada == "ALTERACAO" else "Exclusão")
                    try:
                        validador.check_header()
                        validador.check_ano_mes_ref()

                        if acao_normalizada == "ALTERACAO":
                            validador.check_duplicatas_por_id_atributo()

                        if acao_normalizada == "ALTERACAO":
                            validador.check_atributos()
                            validador.check_id()
                            resultado = validador.validar_alteracao()
                        elif acao_normalizada == "EXCLUSAO":
                            resultado = validador.validar_exclusao()
                        else:
                            resultado = df_filtrado

                        if resultado is not None:
                            ok_count = (resultado['VALIDACAO'] == "OK").sum()
                            processed_rows += ok_count
                            error_count = len(resultado) - ok_count
                            error_rows += error_count
                            resultados.append(resultado)

                    except Exception as e:
                        st.error(f"Erro na validação para {modulo} - {acao}: {str(e)}")
                        continue

            if resultados:
                df_final = pd.concat(resultados, ignore_index=True)
                exibir_resultados(df_final)

                if modulos_nao_reconhecidos:
                    # Obter lista de módulos válidos
                    modulos_validos = list(RegistryValidators._validators_alt_exc.keys())
                    modulos_validos.sort()  # Ordenar alfabeticamente
                    
                    st.error(f"❌ **Módulos não reconhecidos:** {', '.join(modulos_nao_reconhecidos)}")
                    st.info(f"📋 **Módulos válidos disponíveis:** {', '.join(modulos_validos)}")
                    st.warning("As linhas com módulos não reconhecidos foram ignoradas durante a validação.")
                    
                if acao_nao_reconhecida:
                    st.warning(f"As linhas com as ações a seguir não são reconhecidas e por isso foram ignoradas: {', '.join(acao_nao_reconhecida)}. ")
                if (df_final['VALIDACAO'] == 'OK').all():
                    st.success("Validação concluída e sem erros encontrados.")
                    st.toast("Todos os registros estão válidos!", icon="✅")
                    st.balloons()
                else:
                    st.error("Validação concluída, e com erros encontrados.")
                    st.toast("Alguns registros possuem erros!", icon="⚠️")

                oferecer_download(df_final)

                st.divider()
                st.subheader("Relatório de Processamento")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total de Registros", total_rows)
                col2.metric("Registros Válidos", processed_rows)
                col3.metric("Registros com Problemas", error_rows)

            else:
                # Se não há resultados mas há módulos não reconhecidos, mostrar os módulos válidos
                if modulos_nao_reconhecidos:
                    modulos_validos = list(RegistryValidators._validators_alt_exc.keys())
                    modulos_validos.sort()
                    
                    st.error(f"❌ **Módulos não reconhecidos:** {', '.join(modulos_nao_reconhecidos)}")
                    st.info(f"📋 **Módulos válidos disponíveis:** {', '.join(modulos_validos)}")
                else:
                    st.toast("Nenhum registro válido encontrado no arquivo.", icon="⚠️")

        except Exception as e:
            st.error(f"Erro na validação: {str(e)}")

main()
instrucoes_validar_alteracoes_exclusoes()

footer()