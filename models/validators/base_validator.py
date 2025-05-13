import re
import pandas as pd
import streamlit as st
from abc import ABC, abstractmethod
from utils.utils import oferecer_download, exibir_resultados, color_rows
from models.common import CONFIGURACOES_MODULOS
from utils.tratamentos import limpar_dados, padronizar_texto, string_to_float, formata_cpf, formata_cnpj, verificar_formato_brasileiro, validar_data_brasileira

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
                                                 f"{campo}: Formato de data inválido, é esperado AAAA-MM-DD.")

        for campo in self.datas_abreviadas:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor) and not re.match(r'^\d{4}-\d{2}$', str(valor)):
                        self._registrar_erro(idx, f"{campo}: Formato de data abreviada inválido, é esperado AAAA-MM.")

    def validar_campos_obrigatorios(self):
        """Verifica se os campos obrigatórios estão preenchidos"""
        for campo in self.campos_obrigatorios:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    # Verifica se é NaN (nulo) ou string vazia
                    if pd.isna(valor) or (isinstance(valor, str) and not valor.strip()):
                        self._registrar_erro(idx, f"{campo}: Campo obrigatório não preenchido.\n")
            else:
                st.error(f"Campo obrigatório '{campo}' não encontrado no arquivo")
                st.stop()

    def validar_tamanho_campos(self):
        for campo, tamanho_max in self.limites_tamanho.items():
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor) and len(str(valor)) > tamanho_max:
                        self._registrar_erro(idx, f"{campo}: Tamanho máximo excedido, (max {tamanho_max} caracteres).")

    def validar_valores_monetarios(self):
        for campo in self.campos_monetarios:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        try:
                            valor_str = str(valor).strip()

                            padrao_valido = (
                                    re.match(r'^-?\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?$',
                                             valor_str) or
                                    re.match(r'^-?\d+(?:,\d{1,2})?$', valor_str)
                            )

                            if not padrao_valido:
                                self._registrar_erro(idx,
                                                     f"{campo}: Formato inválido, use 1.234,56 ou 1234,56 ou 123")
                                continue

                            valor_convertido = float(valor_str.replace('.', '').replace(',', '.'))

                            if valor_convertido < 0:
                                self._registrar_erro(idx, f"{campo}: Valor negativo")

                        except (ValueError, TypeError):
                            self._registrar_erro(idx, f"{campo}: Valor monetário inválido")

    def validar_tamanho(self):
        pass

    def validar_inteiros(self):
        """Valida se os campos configurados contêm valores inteiros"""
        self.campos_inteiros = getattr(self, 'campos_inteiros', [])
        for campo in self.campos_inteiros:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        try:
                            # Tenta converter para inteiro
                            int(valor)
                            # Verifica se há decimais em valores float
                            if isinstance(valor, float) and not valor.is_integer():
                                raise ValueError
                        except (ValueError, TypeError):
                            self._registrar_erro(idx,
                                                 f"{campo}: Deve ser um número inteiro válido")

    def validar_positivo(self):
        """Valida se os campos configurados contêm valores não negativos"""
        self.campos_positivos = getattr(self, 'campos_positivos', [])
        for campo in self.campos_positivos:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        try:
                            valor_num = float(valor)
                            if valor_num < 0:
                                self._registrar_erro(idx,
                                                     f"{campo}: Não pode ser negativo")
                        except (ValueError, TypeError):
                            self._registrar_erro(idx,
                                                 f"{campo}: Valor numérico inválido")

    def validar_cpf(self):
        self.campos_cpf = getattr(self, 'campos_cpf', [])
        for campo in self.campos_cpf:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        try:
                            valor_split = str(valor).split(' ')[0]
                            if formata_cpf(valor_split) == 'invalido':
                                self._registrar_erro(idx, f"{campo}: CPF inválido")
                        except Exception as e:
                            self._registrar_erro(idx, f"{campo}: Erro na validação - {str(e)}")

    def validar_cnpj(self):
        self.campos_cnpj = getattr(self, 'campos_cnpj', [])
        for campo in self.campos_cnpj:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    print(f"Campo: {campo}, Valor: {valor}")
                    if pd.notna(valor):
                        try:
                            valor_split = str(valor).split(' ')[0]
                            if formata_cnpj(valor_split) == 'invalido':
                                self._registrar_erro(idx, f"{campo}: CNPJ inválido")
                        except Exception as e:
                            self._registrar_erro(idx, f"{campo}: Erro na validação - {str(e)}")

    def validar_nome(self):
        self.campos_nome = getattr(self, 'campos_nome', [])
        for campo in self.campos_nome:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        validacoes = []
                        if not isinstance(valor, str):
                            validacoes.append(f"{campo}: Deve ser texto")
                        else:
                            valor_clean = valor.strip()
                            if len(valor_clean) > 100:
                                validacoes.append(f"{campo}: Máximo 100 caracteres")
                            if not re.fullmatch(r'[a-zA-Z0-9\sà-üÀ-ÜçÇéÉãÃõÕôÔîÎûÛ]+', valor_clean):
                                validacoes.append(f"{campo}: Caracteres inválidos")

                        if validacoes:
                            self._registrar_erro(idx, "\n".join(validacoes))

    def validar_razao_social(self):
        self.campos_razao_social = getattr(self, 'campos_razao_social', [])
        for campo in self.campos_razao_social:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        validacoes = []
                        if not isinstance(valor, str):
                            validacoes.append(f"{campo}: Deve ser texto")
                        else:
                            valor_clean = valor.strip()
                            if len(valor_clean) > 100:
                                validacoes.append(f"{campo}: Máximo 100 caracteres")
                            if not re.fullmatch(r'[a-zA-Z0-9\sà-üÀ-ÜçÇéÉãÃõÕôÔîÎûÛ\.,\-_&/\()\?%]+', valor_clean):
                                validacoes.append(f"{campo}: Caracteres inválidos")

                        if validacoes:
                            self._registrar_erro(idx, "\n".join(validacoes))

    def validar_documentos_pdf(self):
        """Valida colunas que contêm nomes de arquivos PDF"""
        self.campos_pdf = getattr(self, 'campos_pdf', [])
        for campo in self.campos_pdf:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        validacoes = []
                        valor = str(valor).strip()

                        if not isinstance(self.df.at[idx, campo], str):
                            validacoes.append(f'{campo}: Deve ser uma string')

                        if not valor.lower().endswith('.pdf'):
                            validacoes.append(f'{campo}: Deve terminar com .pdf')
                        else:
                            if not valor.endswith('.pdf'):
                                validacoes.append(f'{campo}: Extensão .pdf deve ser minúscula')

                        if len(valor) > 150:
                            validacoes.append(f'{campo}: Tamanho máximo excedido (150 caracteres)')

                        nome_base = valor[:-4] if valor.lower().endswith('.pdf') else valor
                        if not re.fullmatch(r'^[A-Z0-9_]+$', nome_base):
                            validacoes.append(f'{campo}: Deve conter apenas letras maiúsculas, números e underline (_)')

                        if validacoes:
                            self._registrar_erro(idx, '\n'.join(validacoes))

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
            self.df.at[idx, 'VALIDACAO'] += f"\n\n{mensagem}"

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