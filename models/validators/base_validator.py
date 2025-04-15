import re
import pandas as pd
import streamlit as st
from abc import ABC, abstractmethod
from models.common import LISTA_ATRIBUTOS_CONTRATOS_DE_TERCEIROS, LISTA_ATRIBUTOS_DESPESAS

class BaseValidator(ABC):
    def __init__(self, df, tipo_de_acao):
        self.df = df
        self.tipo_de_acao = tipo_de_acao
        self.required_columns = []
        self.valid_attributes = []

    def check_header(self):
        df_cols = set(self.df.columns.str.strip().str.upper())
        required_cols = set(col.strip().upper() for col in self.required_columns)

        missing_cols = required_cols - df_cols
        extra_cols = df_cols - required_cols

        if missing_cols:
            st.error(f"Colunas obrigatórias faltantes: {', '.join(missing_cols)}")
            st.stop()

        if extra_cols:
            st.warning(f"Colunas extras detectadas: {', '.join(extra_cols)}")

    def check_ano_mes_ref(self):
        if 'ANO_MES_REF' not in self.df.columns:
            st.error("Coluna ANO_MES_REF não encontrada")
            st.stop()

        if not all(self.df['ANO_MES_REF'].astype(str).str.match(r'^\d{4}-\d{2}$')):
            st.error("Formato inválido para ANO_MES_REF (deve ser AAAA-MM)")
            st.stop()

        if len(self.df['ANO_MES_REF'].unique()) > 1:
            st.error("Múltiplos períodos de referência na coluna ANO_MES_REF")
            st.stop()

    def check_atributos(self):
        if 'ATRIBUTO' not in self.df.columns:
            st.error("Coluna ATRIBUTO não encontrada")
            st.stop()

        atributos_invalidos = self.df[~self.df['ATRIBUTO'].isin(self.valid_attributes)]['ATRIBUTO'].unique()
        if len(atributos_invalidos) > 0:
            st.error(f"Seu arquivo contém atributos não reconhecidos para o módulo selecionado: {', '.join(atributos_invalidos)}")
            st.success(f"Os atributos válidos para o módulo de {self.df['TIPO_MODULO'].unique()[0]} são: {', '.join(self.valid_attributes)}")
            st.stop()

    def formatar_cpf(self, cpf):
        cpf = re.sub(r'\D', '', cpf)
        if len(cpf) != 11:
            return 'inválido'
        return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'

    def formatar_cnpj(self, cnpj):
        cnpj = re.sub(r'\D', '', cnpj)
        if len(cnpj) != 14:
            return 'inválido'
        return f'{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}'

    @abstractmethod
    def validate_data(self):
        pass