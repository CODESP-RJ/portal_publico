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
from utils.bigquery_utils import validar_datalake
from utils.logging_utils import save_usage_log
from streamlit_app import init_connection

st.markdown("<h1 style='text-align: center;'>Valida arquivos de Alterações/Exclusões</h1>", unsafe_allow_html=True)
st.divider()

def main():
    with st.form('main_form'):
        arquivo = st.file_uploader("Selecione ou arraste um arquivo CSV", type="csv")
        submitted = st.form_submit_button("Processar", width='content')

    if submitted:
        if not arquivo:
            st.error("Selecione um arquivo!")
            st.toast("Nenhum arquivo selecionado!", icon="⚠️")
            return

        try:
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
                
                # Coleta tipos de módulo processados para o log
                tipos_modulo_processados = list(df['TIPO_MODULO'].unique()) if 'TIPO_MODULO' in df.columns else []
                tipo_modulo_str = ', '.join(tipos_modulo_processados) if tipos_modulo_processados else None
                
                # Determina o tipo de funcionalidade baseado nas ações
                acoes_no_arquivo = list(df['ACAO'].unique()) if 'ACAO' in df.columns else []
                tipo_funcionalidade = 'ALTERACAO'
                if 'EXCLUSAO' in [a.upper().strip() for a in acoes_no_arquivo]:
                    if 'ALTERACAO' in [a.upper().strip() for a in acoes_no_arquivo]:
                        tipo_funcionalidade = 'ALTERACAO_EXCLUSAO'  # Ambos no mesmo arquivo
                    else:
                        tipo_funcionalidade = 'EXCLUSAO'
                
                # Salva log de uso
                try:
                    supabase_client = init_connection()
                    save_usage_log(
                        supabase_client=supabase_client,
                        tipo_funcionalidade=tipo_funcionalidade,
                        tipo_modulo=tipo_modulo_str,  # Valores de TIPO_MODULO do arquivo
                        nome_arquivo=arquivo.name if arquivo else None,
                        quantidade_linhas=total_rows
                    )
                except Exception as e:
                    # Não interrompe o fluxo se houver erro no log
                    pass

                if modulos_nao_reconhecidos:
                    modulos_validos = list(RegistryValidators._validators_alt_exc.keys())
                    modulos_validos.sort()
                    
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
                    st.toast("Alguns registros possuem erros!", icon="⚠️")
                    
                    status_container = st.empty()
                    steps_list = []
                    current_step = None
                    
                    def atualizar_status(mensagem, progresso=None):
                        """Atualiza o status das validações com steps"""
                        nonlocal steps_list, current_step
                        
                        mensagem_original = mensagem
                        mensagem_sem_emoji = mensagem.replace("🔌", "").replace("✅", "").replace("📊", "").replace("🔍", "").replace("🔗", "").replace("📋", "").replace("📦", "").replace("✓", "").replace("🎉", "").strip()
                        
                        if "Validando módulo" in mensagem and ":" in mensagem:
                            modulo_nome = mensagem.split(":")[-1].strip()
                            step_label = f"📊 Validando módulo: {modulo_nome}"
                            if not any(step_label == s.get("label") for s in steps_list):
                                steps_list.append({"label": step_label, "status": "running", "substeps": []})
                            current_step = len(steps_list) - 1
                        
                        elif "Verificando se os IDs informados existem" in mensagem or ("Verificando" in mensagem_sem_emoji and "ID" in mensagem_sem_emoji and "existem" in mensagem_sem_emoji):
                            if current_step is not None and current_step < len(steps_list):
                                if "substeps" not in steps_list[current_step]:
                                    steps_list[current_step]["substeps"] = []
                                substep_text = mensagem_sem_emoji.replace("  ", "").strip()
                                if not any(substep_text in s for s in steps_list[current_step]["substeps"]):
                                    steps_list[current_step]["substeps"].append(substep_text)
                        
                        elif "Verificando se os valores informados são válidos" in mensagem:
                            if current_step is not None and current_step < len(steps_list):
                                if "substeps" not in steps_list[current_step]:
                                    steps_list[current_step]["substeps"] = []
                                substep_text = mensagem_sem_emoji.replace("  ", "").strip()
                                if not any(substep_text in s for s in steps_list[current_step]["substeps"]):
                                    steps_list[current_step]["substeps"].append(substep_text)
                        
                        elif "Verificando se" in mensagem_sem_emoji and ("existe" in mensagem_sem_emoji or "existem" in mensagem_sem_emoji):
                            if current_step is not None and current_step < len(steps_list):
                                if "substeps" not in steps_list[current_step]:
                                    steps_list[current_step]["substeps"] = []
                                substep_text = mensagem_sem_emoji.replace("    ", "").strip()
                                if not any(substep_text == s for s in steps_list[current_step]["substeps"]):
                                    steps_list[current_step]["substeps"].append(substep_text)
                        
                        elif "Processando lote" in mensagem:
                            if current_step is not None and current_step < len(steps_list):
                                if "substeps" in steps_list[current_step] and steps_list[current_step]["substeps"]:
                                    lote_info = mensagem_sem_emoji.replace("    ", "").strip()
                                    if steps_list[current_step]["substeps"]:
                                        last = steps_list[current_step]["substeps"][-1]
                                        if "lote" not in last.lower():
                                            steps_list[current_step]["substeps"][-1] = f"{last} ({lote_info})"
                        
                        elif "encontrado(s)" in mensagem_sem_emoji.lower() or ("de" in mensagem_sem_emoji and "ID" in mensagem_sem_emoji and "encontrado" in mensagem_sem_emoji):
                            if current_step is not None and current_step < len(steps_list):
                                if "substeps" in steps_list[current_step] and steps_list[current_step]["substeps"]:
                                    resultado = mensagem_sem_emoji.replace("    ", "").strip()
                                    if steps_list[current_step]["substeps"]:
                                        last = steps_list[current_step]["substeps"][-1]
                                        if "encontrado" not in last.lower():
                                            steps_list[current_step]["substeps"][-1] = f"{last} - {resultado}"
                        
                        elif "validado com sucesso" in mensagem_sem_emoji.lower() or ("Módulo" in mensagem_sem_emoji and "validado" in mensagem_sem_emoji):
                            if current_step is not None and current_step < len(steps_list):
                                steps_list[current_step]["status"] = "complete"
                                steps_list[current_step]["label"] = steps_list[current_step]["label"].replace("📊", "✅")
                        
                        elif "Todas as validações adicionais foram concluídas" in mensagem:
                            steps_list.append({"label": "🎉 Todas as validações adicionais foram concluídas", "status": "complete"})
                        
                        status_title = "🔄 Validação Adicional em andamento..." if steps_list and any(s.get("status") == "running" for s in steps_list) else "✅ Validação Adicional Concluída"
                        with status_container.container():
                            with st.status(status_title, expanded=True):
                                if steps_list:
                                    for step in steps_list:
                                        if step["status"] == "complete":
                                            st.success(step['label'])
                                        else:
                                            st.info(step['label'])
                                            if "substeps" in step and step["substeps"]:
                                                for substep in step["substeps"]:
                                                    st.write(f"   └─ {substep}")
                                else:
                                    st.info("🔄 Aguardando início das validações...")
                    
                    try:
                        atualizar_status("🔄 Iniciando validações adicionais...", 0)                        
                        df_datalake = validar_datalake(df_final.copy(), status_callback=atualizar_status)

                        if steps_list:
                            with status_container.container():
                                with st.status("✅ Validação Adicional Concluída", expanded=True):
                                    for step in steps_list:
                                        if step["status"] == "complete":
                                            st.success(step['label'])
                                        else:
                                            st.info(step['label'])
                                        if "substeps" in step and step["substeps"]:
                                            for substep in step["substeps"]:
                                                st.write(f"   └─ {substep}")
                        
                        df_final = df_datalake
                        
                        st.session_state['df_datalake'] = df_datalake
                        
                        st.session_state['datalake_results'] = {
                            'ids_ok': (df_datalake['VALIDACAO_ADICIONAL'] == 'OK').sum(),
                            'problemas_ids': (df_datalake['VALIDACAO_ADICIONAL'].str.contains('NÃO ENCONTRADO NO BANCO DE DADOS', na=False)).sum(),
                            'problemas_valores': len(df_datalake) - (df_datalake['VALIDACAO_ADICIONAL'] == 'OK').sum() - (df_datalake['VALIDACAO_ADICIONAL'].str.contains('NÃO ENCONTRADO NO BANCO DE DADOS', na=False)).sum(),
                            'df_problemas': df_datalake[df_datalake['VALIDACAO_ADICIONAL'] != 'OK'].copy()
                        }
                    
                    except Exception as e:
                        with status_container.container():
                            with st.status("❌ Erro na Validação do Datalake", expanded=True):
                                for step in steps_list:
                                    if step["status"] == "complete":
                                        st.success(step['label'])
                                    else:
                                        st.info(step['label'])
                                        if "substeps" in step and step["substeps"]:
                                            for substep in step["substeps"]:
                                                st.write(f"   └─ {substep}")
                                st.error(f"Erro: {str(e)}")
                        
                        st.error(f"Erro ao validar no datalake: {str(e)}")
                        st.exception(e)
                    
                    st.divider()

                exibir_resultados(df_final)
                oferecer_download(df_final)

                st.divider()
                st.subheader("Relatório de Processamento")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total de Registros", total_rows)
                col2.metric("Registros Válidos", processed_rows)
                col3.metric("Registros com Problemas", error_rows)
                
                if 'datalake_results' in st.session_state:
                    st.divider()
                    st.markdown("### 🔍 Validação Adicional")

                    resultados_datalake = st.session_state['datalake_results']
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("✅ Validações OK", resultados_datalake['ids_ok'])
                    col2.metric("⚠️ IDs Não Encontrados", resultados_datalake['problemas_ids'])
                    col3.metric("⚠️ Valores Inválidos", resultados_datalake['problemas_valores'])
                    
                    df_problemas_datalake = resultados_datalake['df_problemas']
                    
                    if  df_problemas_datalake.empty:
                        st.balloons()
                    
                    del st.session_state['datalake_results']

            else:
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