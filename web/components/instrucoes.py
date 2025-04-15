import streamlit as st

def instrucoes_validar_importacoes():
    st.markdown("---")
    st.info("""

    ### **✅ Passo a Passo**

    1️⃣ **Selecione** o tipo de arquivo/módulo.

    2️⃣ **Faça o upload** de um arquivo no formato **CSV**.

    3️⃣ **Clique em "Processar".**

    4️⃣ **Aguarde** o processamento.
    """)

def instrucoes_validar_alteracoes_exclusoes():
    st.markdown("---")
    st.info("""

    ### **✅ Passo a Passo**

    1️⃣ **Verifique** se o **ATRIBUTO** está de acordo com os padrões definidos para o **TIPO_MODULO**.  

    2️⃣ **Selecione** a instituição.

    3️⃣ **Faça o upload** de um arquivo no formato **CSV**.

    4️⃣ **Clique em "Processar".**

    5️⃣ **Aguarde** o processamento.
    """)