"""
Utilitários para logging e métricas de uso da aplicação
"""
import streamlit as st
from supabase import Client
from datetime import datetime
import uuid

def get_user_ip():
    """Obtém o endereço IP do usuário"""
    # Tenta obter do session_state (preenchido via componente JavaScript)
    if 'client_ip' in st.session_state:
        ip = st.session_state.client_ip
        if ip and ip != 'unknown' and ip:
            return ip
    
    # Fallback: tenta obter através do contexto do Streamlit
    try:
        ctx = st.runtime.scriptrunner.get_script_run_ctx()
        if ctx:
            if hasattr(ctx, 'headers'):
                headers = ctx.headers
                if headers:
                    ip = headers.get('X-Forwarded-For', '')
                    if ip:
                        ip = str(ip).split(',')[0].strip()
                        if ip:
                            return ip
                    ip = headers.get('X-Real-Ip', '')
                    if ip:
                        return str(ip).strip()
                    ip = headers.get('Remote-Addr', '')
                    if ip:
                        return str(ip).strip()
    except:
        pass
    
    return None

def get_user_agent():
    """Obtém o user agent do usuário"""
    # Tenta obter do session_state (preenchido via componente JavaScript)
    if 'client_user_agent' in st.session_state:
        ua = st.session_state.client_user_agent
        if ua and ua != 'unknown' and ua:
            return ua
    
    # Fallback: tenta obter através do contexto do Streamlit
    try:
        ctx = st.runtime.scriptrunner.get_script_run_ctx()
        if ctx:
            if hasattr(ctx, 'headers'):
                headers = ctx.headers
                if headers:
                    ua = headers.get('User-Agent', '')
                    if ua:
                        return str(ua).strip()
    except:
        pass
    
    return None

def get_or_create_session_id():
    """Obtém ou cria um ID de sessão único"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id

def save_usage_log(
    supabase_client: Client,
    tipo_funcionalidade: str,
    nome_modulo: str = None,
    tipo_modulo: str = None,
    nome_arquivo: str = None,
    quantidade_linhas: int = None
):
    """
    Salva um log de uso da aplicação no Supabase
    
    Args:
        supabase_client: Cliente do Supabase
        tipo_funcionalidade: 'INSERCAO', 'ALTERACAO' ou 'EXCLUSAO'
        nome_modulo: Nome do módulo usado (ex: 'Despesas', 'Folha de Pagamento')
        tipo_modulo: Valores de TIPO_MODULO do arquivo (para alterações/exclusões)
        nome_arquivo: Nome do arquivo processado
        quantidade_linhas: Quantidade de linhas no arquivo
    """
    try:
        # Obtém informações do usuário da sessão
        tipo_usuario = st.session_state.get('tipo_usuario')
        secretaria = st.session_state.get('secretaria_selecionada')
        instituicao_parceira = st.session_state.get('instituicao_selecionada')
        
        if not tipo_usuario:
            # Se o usuário não selecionou o tipo, não salva o log
            return
        
        # Prepara os dados do log
        ip_address = get_user_ip()
        user_agent = get_user_agent()
        
        log_data = {
            'tipo_usuario': tipo_usuario,
            'session_id': get_or_create_session_id(),
            'tipo_funcionalidade': tipo_funcionalidade,
            'created_at': datetime.now().isoformat()
        }
        
        # Adiciona IP e User Agent apenas se foram capturados
        if ip_address:
            log_data['ip_address'] = ip_address
        if user_agent:
            log_data['user_agent'] = user_agent
        
        # Adiciona campos opcionais
        if secretaria:
            log_data['secretaria'] = secretaria
        if instituicao_parceira:
            log_data['instituicao_parceira'] = instituicao_parceira
        if nome_modulo:
            log_data['nome_modulo'] = nome_modulo
        if tipo_modulo:
            log_data['tipo_modulo'] = tipo_modulo
        if nome_arquivo:
            log_data['nome_arquivo'] = nome_arquivo
        if quantidade_linhas is not None:
            log_data['quantidade_linhas'] = quantidade_linhas
        
        # Insere no Supabase
        response = supabase_client.table('app_usage_logs').insert(log_data).execute()
        
        return response
    except Exception as e:
        # Não interrompe o fluxo da aplicação se houver erro no log
        st.error(f"Erro ao salvar log: {str(e)}")
        return None

