import streamlit as st

def instrucoes_validar_insercao():
    st.markdown("---")
    st.info("""

    ### **✅ Passo a Passo**

    1️⃣ **Selecione** o tipo de arquivo/módulo.

    2️⃣ **Faça o upload** de um arquivo **CSV** no formato **UTF-8** com separador "**;**".

    3️⃣ **Clique em "Processar"** e aguarde.
    
    4️⃣ **Clique em "Baixar arquivo".**
    """)

def instrucoes_validar_alteracoes_exclusoes():
    st.markdown("---")
    st.info("""

    ### **✅ Passo a Passo**

    1️⃣ **Faça o upload** de um arquivo **CSV** no formato **UTF-8** com separador "**;**".

    2️⃣ **Clique em "Processar"** e aguarde.

    3️⃣ **Clique em "Baixar arquivo".**
    """)