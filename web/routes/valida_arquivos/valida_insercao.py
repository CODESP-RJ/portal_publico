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
from utils.bigquery_utils import validar_datalake
from utils.logging_utils import save_usage_log
from streamlit_app import init_connection

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
    'Folha de Pagamento': 'MODELO RH EXEMPLO - v3.21.3',
    'Provisionamento': 'MODELO PROV RH EXEMPLO - v3.20.11',
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

# Mapeamento do tipo de arquivo para o nome do módulo usado no datalake
tipo_arquivo_to_modulo_datalake = {
    'Despesas': 'DESPESAS',
    'Contratos de Terceiros': 'CONTRATOS DE TERCEIROS',
    'Saldos': 'SALDOS',
    'Bens Patrimoniados': 'BENS PATRIMONIADOS',
    'Itens de Nota Fiscal': 'ITENS DE NOTA FISCAL',
    'Receitas': 'RECEITAS',
    'Fornecedores': None,  # Não mapeado para datalake ainda
    'Folha de Pagamento': None,  # Não mapeado para datalake ainda
    'Provisionamento': None,  # Não mapeado para datalake ainda
    'Desligamento em Lote': None,  # Não mapeado para datalake ainda
    'Funcionarios': None,  # Não mapeado para datalake ainda
    'Vínculos de Trabalho': None  # Não mapeado para datalake ainda
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
        submitted = st.form_submit_button("Processar", width='content')

    if submitted:
        if not arquivo:
            st.error("Selecione um arquivo!")
            st.toast("Nenhum arquivo selecionado!", icon="⚠️")
            return

        # Descarta resultado de uma execução anterior que possa ter sobrado
        st.session_state.pop('datalake_results', None)

        try:
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
            
            # Salva log de uso
            try:
                supabase_client = init_connection()
                save_usage_log(
                    supabase_client=supabase_client,
                    tipo_funcionalidade='INSERCAO',
                    nome_modulo=selected_type,  # Ex: 'Despesas', 'Folha de Pagamento'
                    nome_arquivo=arquivo.name if arquivo else None,
                    quantidade_linhas=total_rows
                )
            except Exception as e:
                # Não interrompe o fluxo se houver erro no log
                pass

            if not resultados.empty:
                ok_count = (resultados['VALIDACAO'] == "OK").sum()
                processed_rows += ok_count
                error_count = len(resultados) - ok_count
                error_rows += error_count
                df_final = resultados.copy()
                validacao_principal_ok = bool((resultados['VALIDACAO'] == 'OK').all())
                
                if validacao_principal_ok:
                    st.toast("Todos os registros estão válidos!", icon="✅")
                else:
                    st.toast("Alguns registros possuem erros!", icon="⚠️")
                    
                    # Verifica se o módulo está mapeado para o datalake ANTES de criar o modal
                    modulo_datalake = tipo_arquivo_to_modulo_datalake.get(selected_type)
                    if modulo_datalake is not None:
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
                            
                            # Adiciona coluna TIPO_MODULO ao DataFrame para validação do datalake
                            df_para_validacao = df_final.copy()
                            df_para_validacao['TIPO_MODULO'] = modulo_datalake
                            
                            # Para arquivos de inserção, não há ID para validar, apenas valores de referência
                            # A função verificar_ids_no_datalake já trata isso corretamente
                            
                            df_datalake = validar_datalake(df_para_validacao, status_callback=atualizar_status)
                            
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
                            
                            # Remove a coluna TIPO_MODULO antes de mesclar
                            if 'TIPO_MODULO' in df_datalake.columns:
                                df_datalake = df_datalake.drop(columns=['TIPO_MODULO'])
                            
                            # Mescla as validações adicionais com os resultados
                            if 'VALIDACAO_ADICIONAL' in df_datalake.columns:
                                df_final['VALIDACAO_ADICIONAL'] = df_datalake['VALIDACAO_ADICIONAL']
                            
                            df_final = df_datalake
                            
                            st.session_state['df_datalake'] = df_datalake
                            
                            st.session_state['datalake_results'] = {
                                'ids_ok': (df_datalake['VALIDACAO_ADICIONAL'] == 'OK').sum() if 'VALIDACAO_ADICIONAL' in df_datalake.columns else 0,
                                'problemas_ids': (df_datalake['VALIDACAO_ADICIONAL'].str.contains('NÃO ENCONTRADO NO BANCO DE DADOS (OBS: HÁ UM DELAY DE ATUALIZAÇÃO DOS DADOS DE APROXIMADAMENTE 12 HORAS)', regex=False, na=False)).sum() if 'VALIDACAO_ADICIONAL' in df_datalake.columns else 0,
                                'problemas_valores': len(df_datalake) - ((df_datalake['VALIDACAO_ADICIONAL'] == 'OK').sum() if 'VALIDACAO_ADICIONAL' in df_datalake.columns else 0) - ((df_datalake['VALIDACAO_ADICIONAL'].str.contains('NÃO ENCONTRADO NO BANCO DE DADOS (OBS: HÁ UM DELAY DE ATUALIZAÇÃO DOS DADOS DE APROXIMADAMENTE 12 HORAS)', regex=False, na=False)).sum() if 'VALIDACAO_ADICIONAL' in df_datalake.columns else 0),
                                'df_problemas': df_datalake[df_datalake['VALIDACAO_ADICIONAL'] != 'OK'].copy() if 'VALIDACAO_ADICIONAL' in df_datalake.columns else pd.DataFrame()
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
                    else:
                        # Módulo não possui validação adicional - apenas exibe warning e continua
                        st.toast(f"⚠️ O módulo '{selected_type}' ainda não possui validação adicional no datalake.")
                
                # Validação adicional sempre executada, mesmo quando não há erros
                if validacao_principal_ok:
                    # Verifica se o módulo está mapeado para o datalake ANTES de criar o modal
                    modulo_datalake = tipo_arquivo_to_modulo_datalake.get(selected_type)
                    if modulo_datalake is not None:
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
                            
                            # Adiciona coluna TIPO_MODULO ao DataFrame para validação do datalake
                            df_para_validacao = df_final.copy()
                            df_para_validacao['TIPO_MODULO'] = modulo_datalake
                            
                            # Para arquivos de inserção, não há ID para validar, apenas valores de referência
                            # A função verificar_ids_no_datalake já trata isso corretamente
                            
                            df_datalake = validar_datalake(df_para_validacao, status_callback=atualizar_status)
                            
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
                            
                            # Remove a coluna TIPO_MODULO antes de mesclar
                            if 'TIPO_MODULO' in df_datalake.columns:
                                df_datalake = df_datalake.drop(columns=['TIPO_MODULO'])
                            
                            # Mescla as validações adicionais com os resultados
                            if 'VALIDACAO_ADICIONAL' in df_datalake.columns:
                                df_final['VALIDACAO_ADICIONAL'] = df_datalake['VALIDACAO_ADICIONAL']
                            
                            df_final = df_datalake
                            
                            st.session_state['df_datalake'] = df_datalake
                            
                            st.session_state['datalake_results'] = {
                                'ids_ok': (df_datalake['VALIDACAO_ADICIONAL'] == 'OK').sum() if 'VALIDACAO_ADICIONAL' in df_datalake.columns else 0,
                                'problemas_ids': (df_datalake['VALIDACAO_ADICIONAL'].str.contains('NÃO ENCONTRADO NO BANCO DE DADOS (OBS: HÁ UM DELAY DE ATUALIZAÇÃO DOS DADOS DE APROXIMADAMENTE 12 HORAS)', regex=False, na=False)).sum() if 'VALIDACAO_ADICIONAL' in df_datalake.columns else 0,
                                'problemas_valores': len(df_datalake) - ((df_datalake['VALIDACAO_ADICIONAL'] == 'OK').sum() if 'VALIDACAO_ADICIONAL' in df_datalake.columns else 0) - ((df_datalake['VALIDACAO_ADICIONAL'].str.contains('NÃO ENCONTRADO NO BANCO DE DADOS (OBS: HÁ UM DELAY DE ATUALIZAÇÃO DOS DADOS DE APROXIMADAMENTE 12 HORAS)', regex=False, na=False)).sum() if 'VALIDACAO_ADICIONAL' in df_datalake.columns else 0),
                                'df_problemas': df_datalake[df_datalake['VALIDACAO_ADICIONAL'] != 'OK'].copy() if 'VALIDACAO_ADICIONAL' in df_datalake.columns else pd.DataFrame()
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
                    else:
                        # Módulo não possui validação adicional - apenas exibe warning e continua
                        st.toast(f"⚠️ O módulo '{selected_type}' ainda não possui validação adicional no datalake.")
                        
                        st.divider()
                
                exibir_resultados(df_final)
                oferecer_download(df_final)

                st.divider()
                st.subheader("Relatório de Processamento")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total de Registros", total_rows)
                col2.metric("Registros Válidos", processed_rows)
                col3.metric("Registros com Problemas", error_rows)
                
                validacao_adicional_ok = True

                if 'datalake_results' in st.session_state:
                    st.divider()
                    st.markdown("### 🔍 Validação Adicional")
                    
                    resultados_datalake = st.session_state['datalake_results']
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("✅ Validações OK", resultados_datalake['ids_ok'])
                    col2.metric("⚠️ IDs Não Encontrados", resultados_datalake['problemas_ids'])
                    col3.metric("⚠️ Valores Inválidos", resultados_datalake['problemas_valores'])
                    
                    df_problemas_datalake = resultados_datalake['df_problemas']
                    validacao_adicional_ok = df_problemas_datalake.empty
                    
                    if validacao_adicional_ok and not validacao_principal_ok:
                        st.warning(
                            f"⚠️ A validação adicional não encontrou problemas, mas a validação "
                            f"principal apontou {error_rows} registro(s) com erro. "
                            "Corrija-os antes de enviar o arquivo."
                        )
                    
                    del st.session_state['datalake_results']

                # Os balões só sobem quando as duas validações passam
                if validacao_principal_ok and validacao_adicional_ok:
                    st.balloons()

            else:
                st.toast("Nenhum registro válido encontrado no arquivo.", icon="⚠️")

        except Exception as e:
            st.error(f"Erro na validação: {str(e)}")
main()
instrucoes_validar_insercao()

footer()