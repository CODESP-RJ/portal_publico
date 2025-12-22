"""
Componente modal para seleção de tipo de usuário (Secretaria ou Instituição Parceira)
"""
import streamlit as st
from utils.bigquery_utils import get_bigquery_client

# Listas de fallback caso não consiga buscar do datalake
SECRETARIAS_FALLBACK = [
    "SECRETARIA ESPECIAL DE TURISMO",
    "SECRETARIA ESPECIAL DA JUVENTUDE CARIOCA",
    "SECRETARIA ESPECIAL DE INTEGRAÇÃO METROPOLITANA",
    "SECRETARIA MUNICIPAL DO ENVELHECIMENTO SAUDÁVEL E QUALIDADE",
    "SECRETARIA ESPECIAL DE CIDADANIA",
    "SECRETARIA ESPECIAL DE PROTEçãO E DEFESA DO CONSUMIDOR",
    "SECRETARIA MUNICIPAL DE PROTEÇÃO E DEFESA DOS ANIMAIS",
    "SECRETARIA ESPECIAL DE AÇÃO COMUNITÁRIA",
    "SECRETARIA MUNICIPAL DE ASSISTÊNCIA SOCIAL",
    "SECRETARIA MUNICIPAL DA PESSOA COM DEFICIÊNCIA",
    "SECRETARIA ESPECIAL DE POLÍTICAS E PROMOÇÃO DA MULHER",
    "SECRETARIA DO MEIO AMBIENTE",
    "SECRETARIA MUNICIPAL DE SAÚDE",
    "SECRETARIA MUNICIPAL DE CIÊNCIA E TECNOLOGIA",
    "SECRETARIA MUNICIPAL DE EDUCAÇÃO",
    "SECRETARIA MUNICIPAL DE CULTURA",
    "SECRETARIA MUNICIPAL DE ESPORTES",
    "SECRETARIA ESPECIAL DE ECONOMIA SOLIDÁRIA",
    "SECRETARIA MUNICIPAL DE TRABALHO E RENDA",
    "OUTRA SECRETARIA"
]

INSTITUICOES_PARCEIRAS_FALLBACK = [
    "ABRIGO DOCE MORADA",
    "ABRIGO EVANGÉLICO DA PEDRA DE GUARATIBA",
    "AMANHECER AMPARO À INFÂNCIA",
    "ASSISTENCIA SOCIAL NOSSA SENHORA DA CONCEICAO",
    "ASSOCIACAO DE ASSISTENCIA AS CAUSAS SOCIAIS",
    "ASSOCIACAO DE PAIS E AMIGOS DOS EXCEPCIONAIS / APAE-RIO",
    "ASSOCIACAO MARANATHA DO RIO DE JANEIRO - CORDOVIL",
    "ASSOCIACAO MARANATHA DO RIO DE JANEIRO - LINS DE VASCONCELOS",
    "ASSOCIACAO PAR DE ESPORTES, CULTURA E BEM ESTAR",
    "ASSOCIAÇAO SOLIDÁRIOS AMIGOS DE BETÂNIA",
    "ASSOCIAÇÃO ABRAÇO CULTURAL",
    "ASSOCIAÇÃO BALAIO CULTURAL-ABC (SMC)",
    "ASSOCIAÇÃO BENEFICENTE AMAR",
    "ASSOCIAÇÃO CRISTÃ ESPIRITA BENEFICENTE",
    "ASSOCIAÇÃO CULTURAL AMIGOS DO AGITO",
    "ASSOCIAÇÃO MARANATHA DO RIO DE JANEIRO - BANGU",
    "ASSOCIAÇÃO MARANATHA DO RIO DE JANEIRO - MADUREIRA",
    "ASSOCIAÇÃO MARANATHA DO RIO DE JANEIRO - PADRE MIGUEL",
    "ASSOCIAÇÃO MARANATHA DO RIO DE JANEIRO - VILA KENNEDY",
    "ASSOCIAÇÃO MARANATHÁ DO RIO DE JANEIRO",
    "ASSOCIAÇÃO MARCA PARA PROMOÇÃO DE SERVIÇOS",
    "ASSOCIAÇÃO O FEDERAL",
    "ASSOCIAÇÃO PAULISTA PARA O DESENVOLVIMENTO DA MEDICINA",
    "ASSOCIAÇÃO PHABRIKA DE ARTHES-APA",
    "ASSOCIAÇÃO REDES DE DESENVOLVIMENTO DA MARE(SMC)",
    "BIOTECH HUMANA ORGANIZAÇÃO SOCIAL DE SAÚDE",
    "CASA DA CONVIVENCIA NOSSA SENHORA MAE DO BELO AMOR",
    "CEBRAC - CENTRO BRASILEIRO DE AçõES SOCIAIS PARA A CIDADANIA",
    "CENTRAL DE OPORTUNIDADES",
    "CENTRO CARIOCA DE ASSISTENCIA EM REAB. E PROF-CCARP",
    "CENTRO COMUNITÁRIO LIDIA DOS SANTOS",
    "CENTRO DE APOIO AO DEFICIENTE VISUAL DE SAO GONCALO - CADEVISG",
    "CENTRO DE ASSESSORIA AO MOVIMENTO POPULAR-CAMPO",
    "CENTRO DE AÇÕES CULTURAIS ECOLÓGICAS E SOCIAIS DO SUBURBIO CARIOCA - CACESSC",
    "CENTRO DE CRIAçãO DE IMAGEM POPULAR",
    "CENTRO DE ESTIMULACAO E PSICOPEDAGOGIA CRIART",
    "CENTRO DE ESTUDOS E PESQUISAS CIENTIFICAS FRANCISCO ANTONIO DE SALLES",
    "CENTRO DE ESTUDOS E PESQUISAS DR JOÃO AMORIM",
    "CENTRO DE ESTUDOS E PESQUISAS DR. JOÃO AMORIM",
    "CENTRO DE INTEGRACAO EMPRESA ESCOLA DO ESTADO DO RIO DE JANEIRO - CIEE",
    "CENTRO DE INTEGRAÇÃO DE  DESENVOLVIMENTO SUSTENTÁVEL - CIEDS BRASIL",
    "CENTRO DE ORIENTACAO E REABILITACAO BENEFICENTE DE INHAUMA",
    "CENTRO DE REABILITACAO SANTA CECILIA",
    "CENTRO DE REABILITACAO SAO JOSE",
    "CENTRO EDUCACIONAL ANNE SULLIVAN",
    "CENTRO EDUCACIONAL NOSSO MUNDO",
    "CENTRO ESPECIALIZADO DE ATENDIMENTO A CRIANÇA",
    "CENTRO INTEGRADO DE ESTUDO E PROGRAMAS DE DESENVOLVIMENTO SUSTENTáVEL - CIEDS",
    "CONVIDATIVA - INSTITUTO SOCIO-EDUCACIONAL E CULTURAL PARA QUESTOES DA CIDADANIA",
    "CREARTE - CENTRO DE REABILITACAO DO INSTITUTO ANNA FREUD",
    "CRUZ VERMELHA",
    "DESENVOLVIMENTO DE ASSISTENCIA MULTIPLA - DESAM",
    "EMPRESA PÚBLICA DE SAÚDE DO RIO DE JANEIRO S/A - RIOSAUDE",
    "ESPAÇO CIDADANIA E OPORTUNIDADES SOCIAIS",
    "FEDERAÇÃO DE TEATRO ASSOCIATIVO DO ESTADO DO RIO DE JANEIRO-FETAERJ",
    "FUNDAÇÃO PARA O DESENVOLVIMENTO CIENTÍFICO E TECNOLÓGICO EM SAÚDE",
    "GLOBAL",
    "GNOSIS",
    "HOSPITAL E MATERNIDADE THEREZINHA DE JESUS",
    "HOSPITAL MAHATMA GANDHI",
    "IBEEA",
    "ICA - INSTITUTO CARIOCA DE ATIVIDADES",
    "IGEDES INSTITUTO DE GESTAO E DESENVOLVIMENTO (ANTIGO IDEIAS)",
    "INATOS",
    "INSTITUIÇÃO AÇÃO CRISTÃ VICENTE MORETTI",
    "INSTITUIÇÃO LAR MARIA DE LOURDES",
    "INSTITUTO BESOURO DE FOMENTO SOCIAL E PESQUISA",
    "INSTITUTO BRASIL SOCIAL - IBS",
    "INSTITUTO CONSUELO PINHEIRO",
    "INSTITUTO COSTA E SILVA",
    "INSTITUTO CRESCER COM META",
    "INSTITUTO DE ATENÇÃO BÁSICA E AVANÇADA À SAÚDE",
    "INSTITUTO DE DESENVOLVIMENTO E AÇÃO COMUNITARIA - IDACO.",
    "INSTITUTO DE DESENVOLVIMENTO E GESTAO - IDG",
    "INSTITUTO DE DESENVOLVIMENTO E GESTãO IDG (INATIVO)",
    "INSTITUTO DE DESENVOLVIMENTO HUMANO DOM PIXOTE",
    "INSTITUTO DE DESENVOLVIMENTO HUMANO, SOCIAL E CULTURAL GERACAO DA HORA",
    "INSTITUTO DE PESQUISA E PROMOCAO DA SAUDE",
    "INSTITUTO DE PROTECAO E DEFESA ANIMAL EU SOU TESTEMUNHA DO GOLIAS",
    "INSTITUTO DE PSICOLOGIA CLÍNICA EDUCACIONAL E PROFISSIONAL - IPCEP",
    "INSTITUTO DE PSICOLOGIA CLíNICA EDUCACIONAL E PROFISSIONAL",
    "INSTITUTO EVENTOS AMBIENTAIS - IEVA",
    "INSTITUTO FAIR PLAY",
    "INSTITUTO HUMANITAS",
    "INSTITUTO INOVA RIO",
    "INSTITUTO INOVARIO",
    "INSTITUTO MARIA E JOAO ALEIXO",
    "INSTITUTO NACIONAL DE ASSISTÊNCIA TRABALHO OPORTUNIDADES E SAÚDE",
    "INSTITUTO NACIONAL DE DESENVOLVIMENTO HUMANO",
    "INSTITUTO PERTENCER ESTUDOS E PESQUISA EM INCLUSÃO E EDUCACÃO",
    "INSTITUTO REALIZANDO O FUTURO",
    "INSTITUTO RIO CULTURAL",
    "INSTITUTO SESSUB",
    "INSTITUTO SEVERA ROMANA",
    "INSTITUTO SOCIAL FIBRA",
    "INSTITUTO SOCIAL MARCA DE CRISTO",
    "INSTITUTO TIMONEIROS DA VIOLA",
    "INSTITUTO UEVOM",
    "INSTITUTO UNIR SAÚDE",
    "INSTITUTO USINA SOCIAL",
    "IPCEP",
    "IREL - INSTITUTO RIO ESPORTE E LAZER",
    "LAR DE DANIEL CRISTOVAO",
    "LAR DO ANCIÃO NOVA GALILEIA",
    "LAR PEDRO RICHARD",
    "META - INSTITUTO CRESCER COM META",
    "MINHA CASA - ASSOCIAÇÃO CIVIL DE AMPARO AO MENOR",
    "MOVIMENTO CULTURAL SOCIAL",
    "MOVIMENTO DE INTEGRAÇAO CULTURAL-MIC (SMC)",
    "NÚCLEO DE OFICINAS TERAPÊUTICAS",
    "O CLUBE DOS EXCEPCIONAIS",
    "OBRA DO BERÇO",
    "OBRA SOCIAL DE APOIO AO MENOR DA CIDADE DE DEUS",
    "OBRA SOCIAL DONA MECA",
    "OBSERVATÓRIO DE FAVELAS DO RIO DE JANEIRO",
    "ODEON COMPANHIA TEATRAL",
    "ONG CONTATO CENTRO DE PESQUISAS E DE AÇÕES SOCIAIS E CULTURAIS",
    "ORGANIZAÇÃO INSTITUTO NACIONAL DE ASSISTENCIA, TRABALHO - INATOS",
    "OSS GLOBAL",
    "OSS SMSDC",
    "PEOPLE´S PALACE PROJECTS",
    "PONTO SOLIDÁRIO-PS",
    "PUC-RIO",
    "REDE CARIOCA DE RODAS DE SAMBA",
    "REDE DE DESENVOLVIMENTO HUMANO",
    "RPS",
    "SOCIEDADE BENEFICENTE DE ANCHIETA",
    "SOCIEDADE ESPANHOLA DE BENEFICÊNCIA",
    "SODALICIO DA SACRA FAMÍLIA",
    "SPB/BRASIL - SOCIEDADE PESTALOZZI DO BRASIL",
    "SPDM - ASSOCIAÇÃO PAULISTA PARA O DESENVOLVIMENTO DA MEDICINA",
    "UNIR - UNIAO PARA INTEGRACAO E REALIZACAO",
    "UNIÃO DE GRUPO DE ARTISTAS DE TEATRO DA ZONA OESTE - UGAT - ZO (SMC)",
    "UNIÃO ESPORTIVA VILA OLIMPICA DA MARÉ",
    "VIVA RIO",
    "VIVENDAS DA FÉ",
    "OUTRA INSTITUIÇÃO"
]

@st.cache_data(ttl=3600)
def buscar_secretarias():
    """
    Busca as secretarias do datalake
    """
    try:
        client = get_bigquery_client()
        if not client:
            return SECRETARIAS_FALLBACK
        
        query = """
            SELECT DISTINCT secretaria 
            FROM `rj-cvl.adm_contrato_gestao.secretaria` 
            WHERE id_secretaria not in ('8')
            ORDER BY secretaria
        """
        
        query_job = client.query(query)
        resultados = query_job.result()
        
        secretarias = [row.secretaria for row in resultados]
        
        if secretarias:
            secretarias.append("OUTRA SECRETARIA")
            return secretarias
        else:
            return SECRETARIAS_FALLBACK
            
    except Exception as e:
        return SECRETARIAS_FALLBACK

@st.cache_data(ttl=3600)
def buscar_instituicoes():
    """
    Busca as instituições parceiras (OS) do datalake
    """
    try:
        client = get_bigquery_client()
        if not client:
            return INSTITUICOES_PARCEIRAS_FALLBACK
        
        query = """
            SELECT DISTINCT razao_social
            FROM `rj-cvl.adm_contrato_gestao.administracao_unidade` 
            WHERE sigla_tipo = "OS" and cod_unidade not in ('556', '9780', '9779')
            ORDER BY razao_social
        """
        
        query_job = client.query(query)
        resultados = query_job.result()
        
        instituicoes = [row.razao_social for row in resultados]
        
        if instituicoes:
            instituicoes.append("OUTRA INSTITUIÇÃO")
            return instituicoes
        else:
            return INSTITUICOES_PARCEIRAS_FALLBACK
            
    except Exception as e:
        return INSTITUICOES_PARCEIRAS_FALLBACK

def show_user_selection_modal(supabase_client):
    """
    Exibe um modal para o usuário selecionar se é Secretaria ou Instituição Parceira
    
    Args:
        supabase_client: Cliente do Supabase (pode ser None se não disponível)
    
    Returns:
        bool: True se o usuário já selecionou, False caso contrário
    """
    # Verifica se o usuário já selecionou
    if 'tipo_usuario' in st.session_state and st.session_state.tipo_usuario:
        return True
    
    # Cria o modal usando um container
    with st.container():
        st.markdown("""
        <style>
        .user-selection-modal {
            background-color: #f0f2f6;
            padding: 2rem;
            border-radius: 10px;
            border: 2px solid #1f77b4;
            margin: 2rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("### 👤 Identificação do Usuário")
        st.markdown("Por favor, identifique-se para continuar usando a aplicação.")
        st.divider()
        
        # Seleção do tipo de usuário
        tipo_usuario = st.radio(
            "Você é:",
            ["Secretaria", "Instituição Parceira"],
            key="modal_tipo_usuario",
            horizontal=True
        )
        
        # Seleção específica baseada no tipo
        if tipo_usuario == "Secretaria":
            try:
                secretarias = buscar_secretarias()
            except Exception as e:
                st.warning(f"⚠️ Erro ao buscar secretarias do datalake. Usando lista padrão.")
                secretarias = SECRETARIAS_FALLBACK
            
            secretaria_selecionada = st.selectbox(
                "Selecione a Secretaria:",
                secretarias,
                key="modal_secretaria",
                index=None,
                placeholder="Escolha uma secretaria..."
            )
            instituicao_selecionada = None
        else:  # Instituição Parceira
            try:
                instituicoes = buscar_instituicoes()
            except Exception as e:
                st.warning(f"⚠️ Erro ao buscar instituições do datalake. Usando lista padrão.")
                instituicoes = INSTITUICOES_PARCEIRAS_FALLBACK
            
            instituicao_selecionada = st.selectbox(
                "Selecione a Instituição Parceira:",
                instituicoes,
                key="modal_instituicao",
                index=None,
                placeholder="Escolha uma instituição..."
            )
            secretaria_selecionada = None
        
        st.divider()
        
        # Botão de confirmação
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            confirmar = st.button("✅ Confirmar", type="primary", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Processa a confirmação
        if confirmar:
            if tipo_usuario == "Secretaria" and not secretaria_selecionada:
                st.error("Por favor, selecione uma Secretaria.")
                return False
            elif tipo_usuario == "Instituição Parceira" and not instituicao_selecionada:
                st.error("Por favor, selecione uma Instituição Parceira.")
                return False
            
            # Salva na sessão
            st.session_state.tipo_usuario = "SECRETARIA" if tipo_usuario == "Secretaria" else "INSTITUICAO_PARCEIRA"
            if secretaria_selecionada:
                st.session_state.secretaria_selecionada = secretaria_selecionada
            if instituicao_selecionada:
                st.session_state.instituicao_selecionada = instituicao_selecionada
            
            st.success("✅ Identificação confirmada!")
            st.rerun()
            return True
    
    return False

def get_user_info_display():
    """
    Retorna uma string com as informações do usuário para exibição
    """
    if 'tipo_usuario' not in st.session_state or not st.session_state.tipo_usuario:
        return None
    
    tipo = st.session_state.tipo_usuario
    if tipo == "SECRETARIA":
        return f"🏛️ {st.session_state.get('secretaria_selecionada', 'Secretaria')}"
    else:
        return f"🤝 {st.session_state.get('instituicao_selecionada', 'Instituição Parceira')}"

