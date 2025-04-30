import re
import pandas as pd
import streamlit as st
from abc import ABC, abstractmethod
from utils.utils import oferecer_download, exibir_resultados, color_rows

class BaseValidator(ABC):
    def __init__(self, df, tipo_de_acao):
        self.df = df
        self.required_columns = []
        self.valid_attributes = []

    def check_header(self):
        self.required_columns = ['TIPO_MODULO', 'ANO_MES_REF', 'ACAO', 'ID', 'ATRIBUTO', 'NOVO_VALOR']

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

        # Cria coluna VALIDACAO se não existir
        if 'VALIDACAO' not in self.df.columns:
            self.df['VALIDACAO'] = ''

        if len(self.df['ANO_MES_REF'].unique()) > 1:
            st.error("Múltiplos períodos de referência na coluna ANO_MES_REF")
            # Adiciona erro sem sobrescrever validações existentes
            self.df['VALIDACAO'] = self.df['VALIDACAO'].apply(
                lambda x: x + ', ' if x else '') + 'MÚLTIPLOS PERÍODOS DE REFERÊNCIA NA COLUNA ANO_MES_REF'
            st.stop()

        if not all(self.df['ANO_MES_REF'].astype(str).str.match(r'^\d{4}-\d{2}$')):
            st.error("Formato inválido para ANO_MES_REF (deve ser AAAA-MM)")
            # Adiciona erro sem sobrescrever validações existentes
            self.df['VALIDACAO'] = self.df['VALIDACAO'].apply(
                lambda x: x + ', ' if x else '') + 'FORMATO INVÁLIDO PARA ANO_MES_REF (DEVE SER AAAA-MM)'
            st.stop()

    def check_id(self):
        if 'ID' not in self.df.columns:
            st.error("Coluna ID não encontrada")
            st.stop()

        # Cria coluna VALIDACAO se não existir
        if 'VALIDACAO' not in self.df.columns:
            self.df['VALIDACAO'] = ''

        mask = ~self.df['ID'].astype(str).str.match(r'^\d+$')
        # Adiciona erro apenas para os IDs inválidos, sem sobrescrever validações existentes
        self.df.loc[mask, 'VALIDACAO'] = self.df.loc[mask, 'VALIDACAO'].apply(
            lambda x: x + ', ' if x else '') + 'ID INVÁLIDO (DEVE SER NUMÉRICO)'

    def check_atributos(self):
        # Verifica se a coluna ATRIBUTO existe
        if 'ATRIBUTO' not in self.df.columns:
            st.error("Coluna ATRIBUTO não encontrada")
            st.stop()

        # Cria coluna VALIDACAO se não existir
        if 'VALIDACAO' not in self.df.columns:
            self.df['VALIDACAO'] = ''

        # Obtém o tipo de módulo do DataFrame (já normalizado)
        modulo = self.df['TIPO_MODULO'].iloc[0].strip().upper()

        from models.validator_registry import ValidatorRegistry
        if not ValidatorRegistry.get_validator(modulo):
            st.error(f"Módulo '{modulo}' não é suportado")
            st.stop()

        # Obtém os atributos válidos para o módulo
        valid_attributes = self.valid_attributes

        # Identifica atributos inválidos
        mask = ~self.df['ATRIBUTO'].isin(valid_attributes)
        atributos_invalidos = self.df[mask]['ATRIBUTO'].unique()

        if len(atributos_invalidos) > 0:
            # Adiciona erro para atributos inválidos sem sobrescrever validações existentes
            self.df.loc[mask, 'VALIDACAO'] = self.df.loc[mask, 'VALIDACAO'].apply(
                lambda x: x + ', ' if x else '') + f'ATRIBUTO NÃO RECONHECIDO PARA O MÓDULO DE {modulo} (OS ATRIBUTOS VÁLIDOS SÃO: {", ".join(valid_attributes)})'

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

    def preencher_validacao(self, idx, validacoes):
        validacao_existente = self.df.at[idx, 'VALIDACAO'] if 'VALIDACAO' in self.df.columns and pd.notna(
            self.df.at[idx, 'VALIDACAO']) else ''

        novas_validacoes = '\n'.join(validacoes) if validacoes else ''

        if validacao_existente or novas_validacoes:
            self.df.at[idx, 'VALIDACAO'] = '\n'.join(filter(None, [validacao_existente, novas_validacoes]))
        else:
            self.df.at[idx, 'VALIDACAO'] = 'OK'

    @abstractmethod
    def validate_data(self):
        pass