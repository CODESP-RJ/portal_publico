import streamlit as st

st.markdown("""
    <style>
        .metric-box {
            background-color: #f0f9ff;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            border-left: 4px solid #1a5276;
        }
        .feature-card {
            transition: transform 0.2s;
            cursor: pointer;
        }
        .feature-card:hover {
            transform: translateY(-5px);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='border-radius: 10px; text-align: center;'>
        <h1>Sobre a Ferramenta</h1>
    </div>
""", unsafe_allow_html=True)
st.divider()

with st.expander("📌 Introdução", expanded=True):
    st.write("""
    **Solução desenvolvida para otimizar o processo de desbloqueio** do Painel OSINFO, proporcionando:
    - Verificação inteligente e automática dos arquivos
    - Redução de retrabalho
    - Aumento da eficiência
    - Redução de erros humanos
    """)

with st.container(border=True):
    tab1, tab2 = st.tabs(["🔙 Situação Anterior", "🚀 Nova Realidade"])

    with tab1:
        st.error("**Desafios:**")
        st.markdown("""
        - Necessidade de verificação ponto a ponto em arquivos extensos
        - Lentidão na identificação de padrões de inconsistências nos arquivos
        - Alto risco de erros humanos
        """)
        st.caption("_Sistema anterior baseado em intervenção humana integral_")

    with tab2:
        st.success("**Vantagens da Solução:**")
        st.markdown("""
        - Verificação completa e automática dos arquivos
        - Baixo risco de erros humanos
        """)
        st.caption("_Sistema atual com apoio da ferramenta_")

# Seção de Funcionalidades
st.header("⚙️ Funcionalidades Principais", divider="blue")
cols = st.columns(2)
features = [
    {"title": "Validação Automatizada", "icon": "🤖", "desc": "Validação automatizada de arquivos"},
    {"title": "Acesso Facilitado", "icon": "📁", "desc": "Acesso facilitado a tabelas e arquivos auxiliares"},
    {"title": "Tutoriais", "icon": "🧑🏻‍🏫", "desc": "Vídeos explicativos sobre a prestação de contas"},
]

for i, feature in enumerate(features):
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"""
            <div class='feature-card'>
                <h3>{feature['icon']} {feature['title']}</h3>
                <p>{feature['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

st.header("🔧 Como funciona a validação?", divider="blue")
workflow = st.columns(3)
steps = [
    {"icon": "📤", "title": "Upload de Arquivos", "desc": "Envio dos arquivos necessários"},
    {"icon": "🔍", "title": "Análise Automática", "desc": "Verificação automática dos arquivos"},
    {"icon": "📝", "title": "Apontamento de Ajustes", "desc": "Apontamentos nos arquivos quando necessário"},
]

for i, step in enumerate(steps):
    with workflow[i]:
        with st.container(height=230):
            st.markdown(f"<h3 style='text-align: center'>{step['icon']}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center'><strong>{step['title']}</strong><br>{step['desc']}</p>",
                        unsafe_allow_html=True)

st.divider()

with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("images/CGM_SAUDE.png", width=600, use_column_width=True)