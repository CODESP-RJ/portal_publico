"""
Utilitários para conexão e validação com BigQuery
"""
import os
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import toml
import streamlit as st

MODULO_TO_TABLE = {
    'DESPESAS': {
        'dataset': 'adm_contrato_gestao',
        'table': 'despesas',
        'id_column': 'id_documento'
    },
    'CONTRATOS DE TERCEIROS': {
        'dataset': 'adm_contrato_gestao',
        'table': 'contrato_terceiros',
        'id_column': 'id_contrato_terceiro'
    },
    'BENS PATRIMONIADOS': {
        'dataset': 'adm_contrato_gestao',
        'table': 'bem_patrimoniado',
        'id_column': 'id_bem'
    },
    'ITENS DE NOTA FISCAL': {
        'dataset': 'adm_contrato_gestao',
        'table': 'itens_nota_fiscal',
        'id_column': 'id_item_nf'
    },
    'RECEITAS': {
        'dataset': 'adm_contrato_gestao',
        'table': 'receita_dados',
        'id_column': 'id_receita_dados'
    },
    'SALDOS': {
        'dataset': 'adm_contrato_gestao',
        'table': 'saldo_dados',
        'id_column': 'id_saldo_dados'
    }
}

def carregar_credenciais():
    """Carrega as credenciais do arquivo secrets.toml"""
    secrets_path = ".streamlit/secrets.toml"
    
    if not os.path.exists(secrets_path):
        raise FileNotFoundError(f"Arquivo {secrets_path} não encontrado!")
    
    with open(secrets_path, "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            if line.strip().endswith(','):
                line = line.rstrip().rstrip(',')
            cleaned_lines.append(line)
        cleaned_content = '\n'.join(cleaned_lines)
    
    try:
        secrets = toml.loads(cleaned_content)
    except Exception as e:
        secrets = {}
        secrets["google"] = {}
        in_google_section = False
        for line in cleaned_lines:
            line = line.strip()
            if line == "[google]":
                in_google_section = True
                continue
            if line.startswith("[") and line.endswith("]"):
                in_google_section = False
                continue
            if in_google_section and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                secrets["google"][key] = value
    
    if "google" not in secrets:
        raise ValueError("Seção [google] não encontrada no secrets.toml")
    
    google_config = secrets["google"]
    
    def limpar_valor(valor):
        if isinstance(valor, str):
            return valor.replace(",", "").strip().strip('"').strip("'")
        return str(valor).replace(",", "").strip()
    
    credentials_dict = {
        "type": limpar_valor(google_config.get("type", "")),
        "project_id": limpar_valor(google_config.get("project_id", "")),
        "private_key_id": limpar_valor(google_config.get("private_key_id", "")),
        "private_key": limpar_valor(google_config.get("private_key", "")).replace("\\n", "\n"),
        "client_email": limpar_valor(google_config.get("client_email", "")),
        "client_id": limpar_valor(google_config.get("client_id", "")),
        "auth_uri": limpar_valor(google_config.get("auth_uri", "")),
        "token_uri": limpar_valor(google_config.get("token_uri", "")),
        "auth_provider_x509_cert_url": limpar_valor(google_config.get("auth_provider_x509_cert_url", "")),
        "client_x509_cert_url": limpar_valor(google_config.get("client_x509_cert_url", "")),
        "universe_domain": limpar_valor(google_config.get("universe_domain", "googleapis.com"))
    }
    
    return credentials_dict

@st.cache_resource
def get_bigquery_client():
    """Cria e retorna um cliente BigQuery (com cache)"""
    try:
        credentials_dict = carregar_credenciais()
        project_id = credentials_dict["project_id"]
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        client = bigquery.Client(credentials=credentials, project=project_id)
        return client
    except Exception as e:
        st.error(f"Erro ao conectar com BigQuery: {str(e)}")
        return None

def verificar_ids_no_datalake(df, modulo, status_callback=None):
    """
    Verifica se os IDs do DataFrame existem no datalake BigQuery
    
    Args:
        df: DataFrame com coluna 'ID'
        modulo: Nome do módulo (ex: 'DESPESAS' ou 'BENS PATRIMONIADOS')
        status_callback: Função callback para atualizar status (opcional)
    
    Returns:
        DataFrame com coluna adicional 'VALIDACAO_ADICIONAL'
    """
    if df.empty:
        return df
    
    if 'ID' not in df.columns:
        df['VALIDACAO_ADICIONAL'] = 'OK'
        return df
    
    modulo_upper = modulo.strip().upper()
    
    if modulo_upper not in MODULO_TO_TABLE:
        df['VALIDACAO_ADICIONAL'] = f'NO MOMENTO ESTE MÓDULO NÃO É SUPORTADO PELA VALIDAÇÃO ADICIONAL'
        return df
    
    table_config = MODULO_TO_TABLE[modulo_upper]
    dataset_id = table_config['dataset']
    table_id = table_config['table']
    id_column = table_config['id_column']
    
    client = get_bigquery_client()
    if client is None:
        df['VALIDACAO_ADICIONAL'] = 'ERRO AO CONECTAR COM BANCO DE DADOS'
        return df
    
    try:
        # Extrai os IDs únicos do DataFrame
        ids = df['ID'].astype(str).unique().tolist()
        
        if not ids:
            df['VALIDACAO_ADICIONAL'] = 'NENHUM ID PARA VALIDAR'
            return df
        
        if status_callback:
            status_callback(f"    📋 Verificando se {len(ids)} ID(s) existem no Banco de Dados...")
        
        batch_size = 1000
        ids_encontrados = set()
        total_batches = (len(ids) + batch_size - 1) // batch_size
        
        for i in range(0, len(ids), batch_size):
            batch_num = (i // batch_size) + 1
            batch_ids = ids[i:i + batch_size]
            
            if status_callback and total_batches > 1:
                status_callback(f"    📦 Processando lote {batch_num}/{total_batches} ({len(batch_ids)} IDs)...")
            
            ids_str = ', '.join([f"'{id_val}'" for id_val in batch_ids])
            
            query = f"""
                SELECT DISTINCT CAST(`{id_column}` AS STRING) as id
                FROM `{client.project}.{dataset_id}.{table_id}`
                WHERE CAST(`{id_column}` AS STRING) IN ({ids_str})
            """
            
            # Executa a query
            query_job = client.query(query)
            resultados = query_job.result()
            
            # Adiciona os IDs encontrados ao conjunto
            ids_encontrados.update({row.id for row in resultados})
        
        if status_callback:
            status_callback(f"    ✅ {len(ids_encontrados)} de {len(ids)} ID(s) encontrado(s)")
        
        # Adiciona a validação ao DataFrame
        df['VALIDACAO_ADICIONAL'] = df['ID'].astype(str).apply(
            lambda x: 'OK' if x in ids_encontrados else f'ID {x} NÃO ENCONTRADO NO BANCO DE DADOS'
        )
        
        return df
        
    except Exception as e:
        if status_callback:
            status_callback(f"    ❌ Erro ao validar IDs: {str(e)}")
        df['VALIDACAO_ADICIONAL'] = f'ERRO AO VALIDAR: {str(e)}'
        return df

def validar_chave_estrangeira(client, dataset_id, tabela_referencia, campo_referencia, valores, campo_df='valor'):
    """
    Valida se valores existem em uma tabela de referência (chave estrangeira)
    
    Args:
        client: Cliente BigQuery
        dataset_id: Dataset do BigQuery
        tabela_referencia: Nome da tabela de referência
        campo_referencia: Nome do campo na tabela de referência
        valores: Lista de valores para validar
        campo_df: Nome do campo no DataFrame (para mensagens de erro)
    
    Returns:
        Set com os valores encontrados
    """
    if not valores:
        return set()
    
    try:
        # Processa em lotes
        batch_size = 1000
        valores_encontrados = set()
        
        for i in range(0, len(valores), batch_size):
            batch_valores = valores[i:i + batch_size]
            valores_str = ', '.join([f"'{str(v)}'" for v in batch_valores])
            
            query = f"""
                SELECT DISTINCT CAST(`{campo_referencia}` AS STRING) as valor
                FROM `{client.project}.{dataset_id}.{tabela_referencia}`
                WHERE CAST(`{campo_referencia}` AS STRING) IN ({valores_str})
            """
            
            query_job = client.query(query)
            resultados = query_job.result()
            valores_encontrados.update({row.valor for row in resultados})
        
        return valores_encontrados
    except Exception as e:
        st.warning(f"Erro ao validar {campo_df} na tabela {tabela_referencia}: {str(e)}")
        return set()

def validar_chave_estrangeira_case_insensitive(client, dataset_id, tabela_referencia, campo_referencia, valores, campo_df='valor'):
    """
    Valida se valores existem em uma tabela de referência (chave estrangeira)
    Faz busca case-insensitive e com trim para ambos os lados
    
    Args:
        client: Cliente BigQuery
        dataset_id: Dataset do BigQuery
        tabela_referencia: Nome da tabela de referência
        campo_referencia: Nome do campo na tabela de referência
        valores: Lista de valores para validar (já normalizados em uppercase)
        campo_df: Nome do campo no DataFrame (para mensagens de erro)
    
    Returns:
        Set com os valores encontrados (em uppercase)
    """
    if not valores:
        return set()
    
    try:
        # Processa em lotes
        batch_size = 1000
        valores_encontrados = set()
        
        for i in range(0, len(valores), batch_size):
            batch_valores = valores[i:i + batch_size]
            # Cria condições OR para busca case-insensitive
            condicoes = []
            for v in batch_valores:
                v_str = str(v).strip().upper()
                condicoes.append(f"UPPER(TRIM(CAST(`{campo_referencia}` AS STRING))) = '{v_str}'")
            
            where_clause = ' OR '.join(condicoes)
            
            query = f"""
                SELECT DISTINCT UPPER(TRIM(CAST(`{campo_referencia}` AS STRING))) as valor
                FROM `{client.project}.{dataset_id}.{tabela_referencia}`
                WHERE {where_clause}
            """
            
            query_job = client.query(query)
            resultados = query_job.result()
            valores_encontrados.update({row.valor for row in resultados})
        
        return valores_encontrados
    except Exception as e:
        st.warning(f"Erro ao validar {campo_df} na tabela {tabela_referencia}: {str(e)}")
        return set()

def validar_bens_patrimoniados(df, client):
    """Validações específicas para BENS PATRIMONIADOS"""
    erros = []
    
    if 'ATRIBUTO' in df.columns and 'NOVO_VALOR' in df.columns:
        # Validar TIPO (id_bem_tipo) quando o atributo for 'TIPO'
        df_tipo = df[df['ATRIBUTO'].str.upper() == 'TIPO'].copy()
        if not df_tipo.empty:
            cod_tipos = df_tipo['NOVO_VALOR'].dropna().astype(str).unique().tolist()
            if cod_tipos:
                tipos_validos = validar_chave_estrangeira(
                    client, 'adm_contrato_gestao', 'bem_patrimoniado_tipo', 
                    'id_bem_tipo', cod_tipos, 'TIPO'
                )
                for idx, row in df_tipo.iterrows():
                    if pd.notna(row.get('NOVO_VALOR')):
                        cod_tipo = str(row['NOVO_VALOR'])
                        if cod_tipo not in tipos_validos:
                            erros.append(f"ID {row.get('ID', 'N/A')}: TIPO {cod_tipo} não encontrado em bem_patrimoniado_tipo")
    else:
        # Para arquivos de inserção, trabalha com COD_TIPO diretamente
        if 'COD_TIPO' in df.columns:
            cod_tipos = df['COD_TIPO'].dropna().astype(str).unique().tolist()
            if cod_tipos:
                tipos_validos = validar_chave_estrangeira(
                    client, 'adm_contrato_gestao', 'bem_patrimoniado_tipo', 
                    'id_bem_tipo', cod_tipos, 'COD_TIPO'
                )
                for idx, row in df.iterrows():
                    if pd.notna(row.get('COD_TIPO')):
                        cod_tipo = str(row['COD_TIPO'])
                        if cod_tipo not in tipos_validos:
                            erros.append(f"Linha {idx}: COD_TIPO {cod_tipo} não encontrado em bem_patrimoniado_tipo")
        
        # Validar COD_OS e COD_UNIDADE (validam contra cod_unidade na tabela unidade)
        # Nota: A tabela de unidades não está disponível no BigQuery no momento
        # Esta validação está temporariamente desabilitada até que o dataset/tabela esteja disponível
        if 'COD_OS' in df.columns or 'COD_UNIDADE' in df.columns:
            unidades = set()
            if 'COD_OS' in df.columns:
                unidades.update(df['COD_OS'].dropna().astype(str).unique().tolist())
            if 'COD_UNIDADE' in df.columns:
                unidades.update(df['COD_UNIDADE'].dropna().astype(str).unique().tolist())
            
            if unidades:
                unidades_validas = validar_chave_estrangeira(
                    client, 'adm_contrato_gestao', 'administracao_unidade',
                    'cod_unidade', list(unidades), 'COD_UNIDADE'
                )
                for idx, row in df.iterrows():
                    if 'COD_OS' in df.columns and pd.notna(row.get('COD_OS')):
                        cod_os = str(row['COD_OS'])
                        if cod_os not in unidades_validas:
                            erros.append(f"Linha {idx}: COD_OS {cod_os} não encontrado em unidade")
                    if 'COD_UNIDADE' in df.columns and pd.notna(row.get('COD_UNIDADE')):
                        cod_unidade = str(row['COD_UNIDADE'])
                        if cod_unidade not in unidades_validas:
                            erros.append(f"Linha {idx}: COD_UNIDADE {cod_unidade} não encontrado em unidade")
        
        # Validar COD_CONTRATO (valida contra numero_contrato na tabela contrato)
        if 'COD_CONTRATO' in df.columns:
            contratos = df['COD_CONTRATO'].dropna().astype(str).unique().tolist()
            if contratos:
                contratos_validos = validar_chave_estrangeira_case_insensitive(
                    client, 'adm_contrato_gestao', 'contrato',
                    'numero_contrato', contratos, 'COD_CONTRATO'
                )
                for idx, row in df.iterrows():
                    if pd.notna(row.get('COD_CONTRATO')):
                        contrato = str(row['COD_CONTRATO']).strip()
                        if contrato not in contratos_validos:
                            erros.append(f"Linha {idx}: COD_CONTRATO {contrato} não encontrado em contrato")
    
    return erros

def validar_despesas(df, client):
    """Validações específicas para DESPESAS"""
    erros = []
    
    # Para arquivos de alteração, trabalha com ATRIBUTO e NOVO_VALOR
    if 'ATRIBUTO' in df.columns and 'NOVO_VALOR' in df.columns:
        # Validar RUBRICA quando o atributo for 'RUBRICA'
        df_rubrica = df[df['ATRIBUTO'].str.upper() == 'RUBRICA'].copy()
        if not df_rubrica.empty:
            rubricas = df_rubrica['NOVO_VALOR'].dropna().astype(str).unique().tolist()
            if rubricas:
                rubricas_validas = validar_chave_estrangeira(
                    client, 'adm_contrato_gestao', 'rubrica',
                    'id_rubrica', rubricas, 'RUBRICA'
                )
                for idx, row in df_rubrica.iterrows():
                    if pd.notna(row.get('NOVO_VALOR')):
                        rubrica = str(row['NOVO_VALOR'])
                        if rubrica not in rubricas_validas:
                            erros.append(f"ID {row.get('ID', 'N/A')}: RUBRICA {rubrica} não encontrada em rubrica")
        
        # Validar TIPO DE DOCUMENTO quando o atributo for 'TIPO DE DOCUMENTO'
        df_tipo_doc = df[df['ATRIBUTO'].str.upper() == 'TIPO DE DOCUMENTO'].copy()
        if not df_tipo_doc.empty:
            # Normaliza os valores (strip e uppercase) para comparação
            tipos = df_tipo_doc['NOVO_VALOR'].dropna().astype(str).str.strip().str.upper().unique().tolist()
            if tipos:
                tipos_validos = validar_chave_estrangeira_case_insensitive(
                    client, 'adm_contrato_gestao', 'tipo_documento',
                    'tipo_documento', tipos, 'TIPO DE DOCUMENTO'
                )
                for idx, row in df_tipo_doc.iterrows():
                    if pd.notna(row.get('NOVO_VALOR')):
                        tipo = str(row['NOVO_VALOR']).strip().upper()
                        if tipo not in tipos_validos:
                            erros.append(f"ID {row.get('ID', 'N/A')}: TIPO DE DOCUMENTO {tipo} não encontrado em tipo_documento")
        
        # Validar CONTA CORRENTE quando o atributo for 'CONTA CORRENTE'
        df_conta = df[df['ATRIBUTO'].str.upper() == 'CONTA CORRENTE'].copy()
        if not df_conta.empty:
            contas = df_conta['NOVO_VALOR'].dropna().astype(str).unique().tolist()
            if contas:
                query = f"""
                    SELECT DISTINCT CONCAT(CAST(`CODIGO_CC` AS STRING), '-', CAST(`DIGITO_CC` AS STRING)) as conta_formatada
                    FROM `{client.project}.adm_contrato_gestao.conta_bancaria`
                    WHERE `codigo_cc` IS NOT NULL AND `digito_cc` IS NOT NULL
                """
                query_job = client.query(query)
                resultados = query_job.result()
                contas_validas = {row.conta_formatada for row in resultados}
                
                for idx, row in df_conta.iterrows():
                    if pd.notna(row.get('NOVO_VALOR')):
                        conta = str(row['NOVO_VALOR'])
                        if conta not in contas_validas:
                            erros.append(f"ID {row.get('ID', 'N/A')}: CONTA CORRENTE {conta} não encontrada em conta_bancaria")
    else:
        if 'COD_OS' in df.columns or 'COD_UNIDADE' in df.columns:
            unidades = set()
            if 'COD_OS' in df.columns:
                unidades.update(df['COD_OS'].dropna().astype(str).unique().tolist())
            if 'COD_UNIDADE' in df.columns:
                unidades.update(df['COD_UNIDADE'].dropna().astype(str).unique().tolist())
            
            if unidades:
                unidades_validas = validar_chave_estrangeira(
                    client, 'adm_contrato_gestao', 'administracao_unidade',
                    'cod_unidade', list(unidades), 'COD_UNIDADE'
                )
                for idx, row in df.iterrows():
                    if 'COD_OS' in df.columns and pd.notna(row.get('COD_OS')):
                        cod_os = str(row['COD_OS'])
                        if cod_os not in unidades_validas:
                            erros.append(f"Linha {idx}: COD_OS {cod_os} não encontrado em unidade")
                    if 'COD_UNIDADE' in df.columns and pd.notna(row.get('COD_UNIDADE')):
                        cod_unidade = str(row['COD_UNIDADE'])
                        if cod_unidade not in unidades_validas:
                            erros.append(f"Linha {idx}: COD_UNIDADE {cod_unidade} não encontrado em unidade")
        
        # Validar COD_CONTRATO (valida contra numero_contrato na tabela contrato)
        if 'COD_CONTRATO' in df.columns:
            contratos = df['COD_CONTRATO'].dropna().astype(str).unique().tolist()
            if contratos:
                contratos_validos = validar_chave_estrangeira_case_insensitive(
                    client, 'adm_contrato_gestao', 'contrato',
                    'numero_contrato', contratos, 'COD_CONTRATO'
                )
                for idx, row in df.iterrows():
                    if pd.notna(row.get('COD_CONTRATO')):
                        contrato = str(row['COD_CONTRATO']).strip()
                        if contrato not in contratos_validos:
                            erros.append(f"Linha {idx}: COD_CONTRATO {contrato} não encontrado em contrato")
        
        # Validar BANCO (valida contra cod_banco na tabela banco)
        if 'BANCO' in df.columns:
            bancos = df['BANCO'].dropna().astype(str).unique().tolist()
            if bancos:
                bancos_validos = validar_chave_estrangeira(
                    client, 'adm_contrato_gestao', 'banco',
                    'cod_banco', bancos, 'BANCO'
                )
                for idx, row in df.iterrows():
                    if pd.notna(row.get('BANCO')):
                        banco = str(row['BANCO'])
                        if banco not in bancos_validos:
                            erros.append(f"Linha {idx}: BANCO {banco} não encontrado em banco")
        
        # Validar AGENCIA (valida contra numero_agencia na tabela agencia)
        if 'AGENCIA' in df.columns:
            agencias = df['AGENCIA'].dropna().astype(str).unique().tolist()
            if agencias:
                agencias_validas = validar_chave_estrangeira(
                    client, 'adm_contrato_gestao', 'agencia',
                    'numero_agencia', agencias, 'AGENCIA'
                )
                for idx, row in df.iterrows():
                    if pd.notna(row.get('AGENCIA')):
                        agencia = str(row['AGENCIA'])
                        if agencia not in agencias_validas:
                            erros.append(f"Linha {idx}: AGENCIA {agencia} não encontrada em agencia")
        
        # Validar DESPESA (valida contra cod_despesa na tabela de tipos de despesas)
        if 'DESPESA' in df.columns:
            despesas = df['DESPESA'].dropna().astype(str).unique().tolist()
            if despesas:
                despesas_validas = validar_chave_estrangeira_case_insensitive(
                    client, 'adm_contrato_gestao', 'plano_contas',  # ou nome da tabela correta
                    'cod_item_plano_de_contas', despesas, 'DESPESA'
                )
                for idx, row in df.iterrows():
                    if pd.notna(row.get('DESPESA')):
                        despesa = str(row['DESPESA']).strip()
                        if despesa not in despesas_validas:
                            erros.append(f"Linha {idx}: DESPESA {despesa} não encontrada em plano_contas")
        
        # Validar RUBRICA
        if 'RUBRICA' in df.columns:
            rubricas = df['RUBRICA'].dropna().astype(str).unique().tolist()
            if rubricas:
                rubricas_validas = validar_chave_estrangeira(
                    client, 'adm_contrato_gestao', 'rubrica',
                    'id_rubrica', rubricas, 'RUBRICA'
                )
                for idx, row in df.iterrows():
                    if pd.notna(row.get('RUBRICA')):
                        rubrica = str(row['RUBRICA'])
                        if rubrica not in rubricas_validas:
                            erros.append(f"Linha {idx}: RUBRICA {rubrica} não encontrada em rubrica")
        
        # Validar TIPO (TIPO DE DOCUMENTO)
        if 'TIPO' in df.columns:
            tipos = df['TIPO'].dropna().astype(str).str.strip().str.upper().unique().tolist()
            if tipos:
                tipos_validos = validar_chave_estrangeira_case_insensitive(
                    client, 'adm_contrato_gestao', 'tipo_documento',
                    'tipo_documento', tipos, 'TIPO'
                )
                for idx, row in df.iterrows():
                    if pd.notna(row.get('TIPO')):
                        tipo = str(row['TIPO']).strip().upper()
                        if tipo not in tipos_validos:
                            erros.append(f"Linha {idx}: TIPO {tipo} não encontrado em tipo_documento")
        
        # Validar CONTA_CORRENTE
        if 'CONTA_CORRENTE' in df.columns:
            contas = df[df['CONTA_CORRENTE'].notna()]['CONTA_CORRENTE'].astype(str).unique().tolist()
            if contas:
                # Busca contas em ambos os formatos: com hífen (codigo-digito) e sem hífen (codigodigito)
                query = f"""
                    SELECT DISTINCT 
                        CONCAT(CAST(codigo_cc AS STRING), '-', CAST(digito_cc AS STRING)) as conta_com_hifen,
                        CONCAT(CAST(codigo_cc AS STRING), CAST(digito_cc AS STRING)) as conta_sem_hifen
                    FROM `{client.project}.adm_contrato_gestao.conta_bancaria`
                    WHERE codigo_cc IS NOT NULL AND digito_cc IS NOT NULL
                """
                query_job = client.query(query)
                resultados = query_job.result()
                contas_validas = set()
                for row in resultados:
                    contas_validas.add(row.conta_com_hifen)
                    contas_validas.add(row.conta_sem_hifen)
                
                for idx, row in df.iterrows():
                    if pd.notna(row.get('CONTA_CORRENTE')):
                        conta = str(row['CONTA_CORRENTE'])
                        if conta not in contas_validas:
                            erros.append(f"Linha {idx}: CONTA_CORRENTE {conta} não encontrada em conta_bancaria")
    
    return erros

def validar_contratos_terceiros(df, client):
    """Validações específicas para CONTRATOS DE TERCEIROS"""
    erros = []
    
    return erros

def validar_itens_nota_fiscal(df, client):
    """Validações específicas para ITENS DE NOTA FISCAL"""
    erros = []
    
    # Para arquivos de alteração, valida FORNECEDOR quando o atributo for 'FORNECEDOR'
    if 'ATRIBUTO' in df.columns and 'NOVO_VALOR' in df.columns:
        df_fornecedor = df[df['ATRIBUTO'].str.upper() == 'FORNECEDOR'].copy()
        if not df_fornecedor.empty:
            fornecedores = df_fornecedor['NOVO_VALOR'].dropna().astype(str).unique().tolist()
            if fornecedores:
                # Busca fornecedores por nome (assumindo que FORNECEDOR é o nome/razão social)
                query = f"""
                    SELECT DISTINCT LOWER(TRIM(`razao_social`)) as razao_social_lower
                    FROM `{client.project}.adm_contrato_gestao.fornecedor`
                """
                query_job = client.query(query)
                resultados = query_job.result()
                fornecedores_validos = {row.razao_social_lower for row in resultados}
                
                for idx, row in df_fornecedor.iterrows():
                    if pd.notna(row.get('NOVO_VALOR')):
                        fornecedor = str(row['NOVO_VALOR']).strip().lower()
                        if fornecedor not in fornecedores_validos:
                            erros.append(f"ID {row.get('ID', 'N/A')}: FORNECEDOR '{row['NOVO_VALOR']}' não encontrado em fornecedor")
    else:
        # Para arquivos de inserção
        if 'FORNECEDOR' in df.columns:
            fornecedores = df[df['FORNECEDOR'].notna()]['FORNECEDOR'].astype(str).unique().tolist()
            if fornecedores:
                query = f"""
                SELECT DISTINCT LOWER(TRIM(`razao_social`)) as razao_social_lower
                FROM `{client.project}.adm_contrato_gestao.fornecedor`
                """
                query_job = client.query(query)
                resultados = query_job.result()
                fornecedores_validos = {row.razao_social_lower for row in resultados}
                
                for idx, row in df.iterrows():
                    if pd.notna(row.get('FORNECEDOR')):
                        fornecedor = str(row['FORNECEDOR']).strip().lower()
                        if fornecedor not in fornecedores_validos:
                            erros.append(f"Linha {idx}: FORNECEDOR '{row['FORNECEDOR']}' não encontrado em fornecedor")
    
    return erros

def aplicar_validacoes_adicionais(df, modulo, client, status_callback=None):
    """
    Aplica validações adicionais específicas para cada módulo
    
    Args:
        df: DataFrame com os dados
        modulo: Nome do módulo (ex: 'BENS PATRIMONIADOS')
        client: Cliente BigQuery
        status_callback: Função callback para atualizar status (opcional)
    
    Returns:
        Lista de erros encontrados
    """
    modulo_upper = modulo.strip().upper()
    erros = []
    
    try:
        if modulo_upper == 'BENS PATRIMONIADOS':
            if status_callback:
                status_callback(f"    ✓ Verificando se o código do TIPO de bem existe na lista de tipos cadastrados...")
            erros = validar_bens_patrimoniados(df, client)
        elif modulo_upper == 'DESPESAS':
            # Verifica quais atributos precisam ser validados
            atributos_para_validar = []
            if 'ATRIBUTO' in df.columns:
                atributos_unicos = df['ATRIBUTO'].str.upper().unique()
                if 'RUBRICA' in atributos_unicos:
                    atributos_para_validar.append('RUBRICA')
                if 'TIPO DE DOCUMENTO' in atributos_unicos:
                    atributos_para_validar.append('TIPO DE DOCUMENTO')
                if 'CONTA CORRENTE' in atributos_unicos:
                    atributos_para_validar.append('CONTA CORRENTE')
            else:
                # Para inserção, valida todos os campos disponíveis
                atributos_para_validar = ['COD_OS', 'COD_UNIDADE', 'COD_CONTRATO', 'BANCO', 'AGENCIA', 'DESPESA', 'RUBRICA', 'TIPO DE DOCUMENTO', 'CONTA CORRENTE']
            
            for attr in atributos_para_validar:
                if attr == 'COD_OS' or attr == 'COD_UNIDADE':
                    if status_callback:
                        status_callback(f"    ✓ Verificando se o código da unidade existe na lista de unidades cadastradas...")
                elif attr == 'COD_CONTRATO':
                    if status_callback:
                        status_callback(f"    ✓ Verificando se o código do contrato existe na lista de contratos cadastrados...")
                elif attr == 'BANCO':
                    if status_callback:
                        status_callback(f"    ✓ Verificando se o código do banco existe na lista de bancos cadastrados...")
                elif attr == 'AGENCIA':
                    if status_callback:
                        status_callback(f"    ✓ Verificando se o número da agência existe na lista de agências cadastradas...")
                elif attr == 'DESPESA':
                    if status_callback:
                        status_callback(f"    ✓ Verificando se o código da despesa existe na lista de despesas cadastradas...")
                elif attr == 'RUBRICA':
                    if status_callback:
                        status_callback(f"    ✓ Verificando se o código da RUBRICA existe na lista de rubricas cadastradas...")
                elif attr == 'TIPO DE DOCUMENTO':
                    if status_callback:
                        status_callback(f"    ✓ Verificando se o código do TIPO DE DOCUMENTO existe na lista de tipos cadastrados...")
                elif attr == 'CONTA CORRENTE':
                    if status_callback:
                        status_callback(f"    ✓ Verificando se a CONTA CORRENTE existe na lista de contas bancárias cadastradas...")
            
            erros = validar_despesas(df, client)
        elif modulo_upper == 'CONTRATOS DE TERCEIROS':
            erros = validar_contratos_terceiros(df, client)
        elif modulo_upper == 'ITENS DE NOTA FISCAL':
            if status_callback:
                status_callback(f"    ✓ Verificando se o nome do FORNECEDOR existe na lista de fornecedores cadastrados...")
            erros = validar_itens_nota_fiscal(df, client)
        # RECEITAS e SALDOS podem ser adicionados depois se necessário
    except Exception as e:
        erros.append(f"Erro ao validar {modulo_upper}: {str(e)}")
    
    return erros

def validar_datalake(df_resultado, status_callback=None):
    """
    Valida todos os módulos do DataFrame resultado contra o datalake
    Inclui validação de IDs e validações de chaves estrangeiras
    
    Args:
        df_resultado: DataFrame com colunas TIPO_MODULO, ID, etc.
        status_callback: Função callback para atualizar status (opcional)
    
    Returns:
        DataFrame com validação adicional do datalake
    """
    if df_resultado.empty:
        return df_resultado
    
    if status_callback:
        status_callback("🔌 Estabelecendo conexão com o datalake...", 5)
    
    client = get_bigquery_client()
    if client is None:
        df_resultado['VALIDACAO_ADICIONAL'] = 'ERRO AO CONECTAR COM BANCO DE DADOS'
        return df_resultado
    
    resultados_datalake = []
    modulos = df_resultado['TIPO_MODULO'].unique()
    total_modulos = len(modulos)
    
    for idx_modulo, modulo in enumerate(modulos, 1):
        progresso_base = 10 + (idx_modulo - 1) * (80 / total_modulos)
        
        if status_callback:
            status_callback(f"📊 Validando módulo {idx_modulo}/{total_modulos}: {modulo}", int(progresso_base))
        
        df_modulo = df_resultado[df_resultado['TIPO_MODULO'] == modulo].copy()
        
        # Validação de IDs
        if status_callback:
            status_callback(f"  🔍 Verificando se os IDs informados existem no datalake...", int(progresso_base + 5))
        df_validado = verificar_ids_no_datalake(df_modulo, modulo, status_callback)
        
        # Validações adicionais de valores de referência
        if status_callback:
            status_callback(f"  🔗 Verificando se os valores informados são válidos...", int(progresso_base + 10))
        erros_adicionais = aplicar_validacoes_adicionais(df_validado, modulo, client, status_callback)
        
        # Adiciona erros encontrados na validação adicional
        if erros_adicionais:
            # Cria uma coluna para erros adicionais ou adiciona aos erros existentes
            if 'VALIDACAO_ADICIONAL' not in df_validado.columns:
                df_validado['VALIDACAO_ADICIONAL'] = 'OK'
            
            # Agrupa erros por ID (para arquivos de alteração) ou por índice (para inserção)
            erros_por_id = {}
            erros_por_idx = {}
            
            for erro in erros_adicionais:
                if 'ID ' in erro and ': ' in erro:
                    # Formato: "ID 123: RUBRICA 456 não encontrada..."
                    id_part = erro.split('ID ')[1].split(':')[0].strip()
                    msg_erro = erro.split(': ', 1)[1] if ': ' in erro else erro
                    if id_part not in erros_por_id:
                        erros_por_id[id_part] = []
                    erros_por_id[id_part].append(msg_erro)
                elif 'Linha ' in erro and ': ' in erro:
                    # Formato: "Linha 0: RUBRICA 456 não encontrada..."
                    idx_part = int(erro.split('Linha ')[1].split(':')[0].strip())
                    msg_erro = erro.split(': ', 1)[1] if ': ' in erro else erro
                    if idx_part not in erros_por_idx:
                        erros_por_idx[idx_part] = []
                    erros_por_idx[idx_part].append(msg_erro)
            
            # Aplica erros por ID (arquivos de alteração)
            if 'ID' in df_validado.columns and erros_por_id:
                for idx, row in df_validado.iterrows():
                    id_val = str(row.get('ID', ''))
                    if id_val in erros_por_id:
                        erro_msg = '; '.join(erros_por_id[id_val])
                        if df_validado.at[idx, 'VALIDACAO_ADICIONAL'] == 'OK':
                            df_validado.at[idx, 'VALIDACAO_ADICIONAL'] = erro_msg
                        else:
                            df_validado.at[idx, 'VALIDACAO_ADICIONAL'] += f'; {erro_msg}'
            
            # Aplica erros por índice (arquivos de inserção)
            if erros_por_idx:
                for idx, msgs in erros_por_idx.items():
                    if idx < len(df_validado):
                        erro_msg = '; '.join(msgs)
                        if df_validado.at[idx, 'VALIDACAO_ADICIONAL'] == 'OK':
                            df_validado.at[idx, 'VALIDACAO_ADICIONAL'] = erro_msg
                        else:
                            df_validado.at[idx, 'VALIDACAO_ADICIONAL'] += f'; {erro_msg}'
        
        resultados_datalake.append(df_validado)
        
        if status_callback:
            progresso_final_modulo = 10 + (idx_modulo) * (80 / total_modulos)
            status_callback(f"  ✅ Módulo {modulo} validado com sucesso!", int(progresso_final_modulo))
       
    if resultados_datalake:
        return pd.concat(resultados_datalake, ignore_index=True)
    
    return df_resultado

