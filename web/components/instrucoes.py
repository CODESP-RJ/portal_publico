import streamlit as st

def instrucoes_validar_importacoes():
    st.markdown("---")
    st.info("""

    ###### ℹ️ **Este módulo verifica se o arquivo está formatado corretamente e se há imagem no osinfo.**

    ⚠️ **Se ocorrer algum erro em qualquer etapa, reporte ao desenvolvedor responsável e capture uma imagem (print) antes de atualizar a página.**

    ### **✅ Passo a Passo**

    1️⃣ **Selecione** o tipo de arquivo/módulo.

    2️⃣ **Faça o upload** de um arquivo no formato **CSV**.

    3️⃣ **Clique em "Processar".**

    4️⃣ **Aguarde** o processamento.
    """)

def instrucoes_validar_alteracoes():
    st.markdown("---")
    st.info("""

    ###### ℹ️ **Este módulo valida se há imagem no osinfo.**

    ⚠️ **Se ocorrer algum erro em qualquer etapa, reporte ao desenvolvedor responsável e capture uma imagem (print) antes de atualizar a página.**

    ### **✅ Passo a Passo**

    1️⃣ **Verifique** se o **ATRIBUTO** está de acordo com os padrões definidos para o **TIPO_MODULO**.  
       - Modelos disponíveis: [📂 Google Drive](https://drive.google.com/drive/u/1/folders/18iWis2JHzRyYJPcFu6vBRhbPyFzpAl6C)

    2️⃣ **Selecione** a instituição.

    3️⃣ **Faça o upload** de um arquivo nos formatos **CSV, XLS ou XLSX**.

    4️⃣ **Clique em "Processar".**

    5️⃣ **Aguarde** o processamento.
    """)