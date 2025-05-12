import re
import pandas as pd
import streamlit as st
from abc import ABC, abstractmethod
from utils.utils import oferecer_download, exibir_resultados, color_rows
from models.common import CONFIGURACOES_MODULOS

class BaseValidatorIns(ABC):
    def __init__(self, df):
        self.df = df
        self.cabecalho_str = ''
        self.cabecalho = []
        self.datas_abreviadas = []
        self.datas_completas = []
        self.campos_obrigatorios = []
        self.campos_monetarios = []
        self.limites_tamanho = {}
        self.erros = pd.DataFrame(columns=['Index', 'Erro'])

    def validar_tudo(self):
        self.validar_comum()
        self.validar_especifico()

    def validar_comum(self):
        """Validações comuns a todos os módulos"""
        self.validar_cabecalho()
        if 'VALIDACAO' in self.df.columns:
            self.df['VALIDACAO'] = 'OK'
        else:
            self.df.insert(len(self.df.columns), 'VALIDACAO', 'OK')
        self.validar_campos_obrigatorios()

    def validar_especifico(self):
        pass

    def validar_datas(self):
        """Valida o formato das datas para todos os campos de data"""
        for campo in self.datas_completas:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        try:
                            # Tenta converter para datetime com inferência automática
                            pd.to_datetime(valor, errors='raise')
                            print(pd.to_datetime(valor, errors='raise'))
                        except ValueError:
                            print(f"Erro de conversão em {campo} com valor {valor} idx {idx}")
                            self._registrar_erro(idx,
                                                 f"Formato de data inválido em {campo}. Esperado dd-mm-yyyy ou yyyy-mm-dd")

        # Valida datas abreviadas (AAAAMM)
        for campo in self.datas_abreviadas:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor) and not re.match(r'^\d{6}$', str(valor)):
                        self._registrar_erro(idx, f"Formato de data abreviada inválido em {campo}. Esperado AAAAMM")

    def validar_campos_obrigatorios(self):
        """Verifica se os campos obrigatórios estão preenchidos"""
        for campo in self.campos_obrigatorios:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    # Verifica se é NaN (nulo) ou string vazia
                    if pd.isna(valor) or (isinstance(valor, str) and not valor.strip()):
                        self._registrar_erro(idx, f"Campo obrigatório '{campo}' não preenchido")
            else:
                st.error(f"Campo obrigatório '{campo}' não encontrado no arquivo")
                st.stop()

    def validar_tamanho_campos(self):
        for campo, tamanho_max in self.limites_tamanho.items():
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor) and len(str(valor)) > tamanho_max:
                        self._registrar_erro(idx, f"Tamanho máximo excedido em {campo} (max {tamanho_max} caracteres)")

    def validar_valores_monetarios(self):
        for campo in self.campos_monetarios:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        try:
                            # Converte para string e trata valores monetários
                            valor_str = str(valor).strip()
                            if valor_str:  # Só valida se não for string vazia
                                # Remove pontos de milhares e substitui vírgula decimal por ponto
                                valor_float = float(valor_str.replace('.', '').replace(',', '.'))
                                if valor_float < 0:
                                    self._registrar_erro(idx, f"Valor monetário negativo em {campo}")
                        except (ValueError, TypeError):
                            self._registrar_erro(idx, f"Valor monetário inválido em {campo}")

    def validar_tamanho(self):
        pass

    def validar_inteiros(self):
        pass

    def validar_cabecalho(self):
        uploaded_columns = [col.strip().replace(" ", "").upper() for col in self.df.columns.tolist()]
        expected_columns = [col.strip().replace(" ", "").upper() for col in self.cabecalho]

        missing_columns = []
        for required_col in [col.strip().replace(" ", "").upper() for col in self.campos_obrigatorios]:
            if required_col not in uploaded_columns:
                missing_columns.append(required_col)

        if missing_columns:
            st.error(f"❌ Colunas obrigatórias faltantes: {', '.join(missing_columns)}")
            st.stop()

        extra_columns = [col for col in uploaded_columns if col not in expected_columns]
        if extra_columns:
            st.warning(f"⚠️ Colunas extras/não reconhecidas: {', '.join(extra_columns)}")
            st.stop()

    def check_columns(self, columns):
        matched_columns = []
        for column in self.df.columns:
            if column in columns:
                matched_columns.append(column)
        return matched_columns

    def retorna_cabecalho(self):
        if not self.cabecalho:
            self.cabecalho = self.trata_cabecalho(self.cabecalho_str)
        return self.cabecalho

    def contem_cabecalho(self, cabecalho_modelo, cabecalho_arquivo):
        todos_contidos = all(item in cabecalho_arquivo for item in cabecalho_modelo)
        if todos_contidos:
            return True
        else:
            return False

    def obter_resultados(self):
        """Retorna os resultados da validação"""
        return self.df

    def _registrar_erro(self, idx, mensagem):
        """Registra um erro na linha específica do DataFrame"""
        if pd.isna(self.df.at[idx, 'VALIDACAO']) or self.df.at[idx, 'VALIDACAO'] == 'OK':
            self.df.at[idx, 'VALIDACAO'] = mensagem
        else:
            self.df.at[idx, 'VALIDACAO'] += f"; {mensagem}"

    @staticmethod
    def trata_cabecalho(cabecalho):
        cabecalho_tratado = cabecalho
        cabecalho_tratado = cabecalho_tratado.replace(" ","").strip('\r\n').upper()
        cabecalho_tratado = cabecalho_tratado.split(";")
        return cabecalho_tratado

    def configurar_modulo(self, nome_modulo):
        if nome_modulo not in CONFIGURACOES_MODULOS:
            raise ValueError(f"Módulo {nome_modulo} não encontrado nas configurações")

        config = CONFIGURACOES_MODULOS[nome_modulo]
        self.cabecalho = self.trata_cabecalho(config['cabecalho_str'])
        self.datas_abreviadas = config['datas_abreviadas']

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
            st.warning(f"Colunas extras/não reconhecidas: {', '.join(extra_cols)}")

    def check_ano_mes_ref(self):
        if 'ANO_MES_REF' not in self.df.columns:
            st.error("Coluna ANO_MES_REF não encontrada")
            st.stop()

        if 'VALIDACAO' not in self.df.columns:
            self.df['VALIDACAO'] = ''

        if len(self.df['ANO_MES_REF'].unique()) > 1:
            st.error("Múltiplos períodos de referência na coluna ANO_MES_REF")
            self.df['VALIDACAO'] = self.df['VALIDACAO'].apply(
                lambda x: x + ', ' if x else '') + 'MÚLTIPLOS PERÍODOS DE REFERÊNCIA NA COLUNA ANO_MES_REF'
            st.stop()

        if not all(self.df['ANO_MES_REF'].astype(str).str.match(r'^\d{4}-\d{2}$')):
            st.error("Formato inválido para ANO_MES_REF (deve ser AAAA-MM)")
            self.df['VALIDACAO'] = self.df['VALIDACAO'].apply(
                lambda x: x + ', ' if x else '') + 'FORMATO INVÁLIDO PARA ANO_MES_REF (DEVE SER AAAA-MM)'
            st.stop()

    def check_id(self):
        if 'ID' not in self.df.columns:
            st.error("Coluna ID não encontrada")
            st.stop()

        if 'VALIDACAO' not in self.df.columns:
            self.df['VALIDACAO'] = ''

        mask = ~self.df['ID'].astype(str).str.match(r'^\d+$')
        self.df.loc[mask, 'VALIDACAO'] = self.df.loc[mask, 'VALIDACAO'].apply(
            lambda x: x + ', ' if x else '') + 'ID INVÁLIDO (DEVE SER NUMÉRICO)'

    def check_atributos(self):
        if 'ATRIBUTO' not in self.df.columns:
            st.error("Coluna ATRIBUTO não encontrada")
            st.stop()

        if 'VALIDACAO' not in self.df.columns:
            self.df['VALIDACAO'] = ''

        modulo = self.df['TIPO_MODULO'].iloc[0].strip().upper()

        from models.registry import RegistryValidators
        if not RegistryValidators.get_validator_alt_exc(modulo):
            st.error(f"Módulo '{modulo}' não é suportado")
            st.stop()

        valid_attributes = self.valid_attributes

        mask = ~self.df['ATRIBUTO'].isin(valid_attributes)
        atributos_invalidos = self.df[mask]['ATRIBUTO'].unique()

        if len(atributos_invalidos) > 0:

            self.df.loc[mask, 'VALIDACAO'] = self.df.loc[mask, 'VALIDACAO'].apply(
                lambda x: x + ', ' if x else '') + f'ATRIBUTO NÃO RECONHECIDO PARA O MÓDULO DE {modulo} (OS ATRIBUTOS VÁLIDOS SÃO: {", ".join(valid_attributes)})'

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