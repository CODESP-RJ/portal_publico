import re
import pandas as pd
import streamlit as st
from abc import ABC, abstractmethod
from utils.utils import oferecer_download, exibir_resultados, color_rows
from models.common import CONFIGURACOES_MODULOS
from utils.tratamentos import limpar_dados, padronizar_texto, string_to_float, formata_cpf, formata_cnpj, verificar_formato_brasileiro, validar_data_brasileira, validar_formato_contrato, valida_cnpj, valida_cpf, valida_cpf

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
        self.validar_apostrofo()
        self.validar_periodo_referencia_unico()
        self.validar_contrato_unico()
        if 'VALIDACAO' in self.df.columns:
            self.df['VALIDACAO'] = 'OK'
        else:
            self.df.insert(len(self.df.columns), 'VALIDACAO', 'OK')
        self.validar_campos_obrigatorios()

    def validar_especifico(self):
        pass

    def validar_apostrofo(self):
        linhas_com_apostrofo = []
        for idx, row in self.df.iterrows():
            for valor in row:
                if pd.notna(valor) and "'" in str(valor):
                    linhas_com_apostrofo.append(idx)
                    break

        if linhas_com_apostrofo:
            st.error(
                f"Erro: O arquivo contém apostrofos (') nas linhas: {', '.join(str(i+1) for i in linhas_com_apostrofo)}. "
                "Remova todos os apostrofos do arquivo antes de prosseguir."
            )
            st.stop()

    def validar_periodo_referencia_unico(self):
        """Verifica se as colunas de datas_abreviadas possuem apenas um único valor em todas as linhas"""
        if not self.datas_abreviadas:
            return
            
        for campo in self.datas_abreviadas:
            if campo in ['CONTRATO_ANO_MES_INICIO', 'CONTRATO_ANO_MES_FIM']:
                pass
            if campo in self.df.columns:
                valores_unicos = self.df[campo].unique()
                if len(valores_unicos) > 1:
                    valores_str = ", ".join([str(v) for v in valores_unicos])
                    st.error(
                        f"Erro: A coluna '{campo}' possui múltiplos valores diferentes: [{valores_str}]. "
                        f"Todos os registros devem ter exatamente o mesmo período de referência."
                    )
                    st.stop()

    def validar_contrato_unico(self):
        """Verifica se a coluna de contrato possui apenas um único valor em todas as linhas"""
        if not hasattr(self, 'campo_contrato') or not self.campo_contrato:
            return
            
        for campo in self.campo_contrato:
            if campo in self.df.columns:
                valores_unicos = self.df[campo].unique()
                if len(valores_unicos) > 1:
                    valores_str = ", ".join([str(v) for v in valores_unicos])
                    st.error(
                        f"Erro: A coluna '{campo}' possui múltiplos contratos diferentes: [{valores_str}]. "
                        f"Todos os registros devem pertencer ao mesmo contrato."
                    )
                    st.stop()

    def validar_datas(self):
        """Valida o formato das datas para todos os campos de data"""
        if not self.datas_completas and not self.datas_abreviadas:
            return
        for campo in self.datas_completas:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        str_valor = str(valor).strip()
                        if not re.match(r'^\d{4}-\d{2}-\d{2}$', str_valor):
                            self._registrar_erro(idx, f"{campo}: Formato inválido. Use AAAA-MM-DD.")
                        else:
                            try:
                                pd.to_datetime(str_valor, format='%Y-%m-%d', errors='raise')
                            except ValueError:
                                self._registrar_erro(idx, f"{campo}: Data inválida (ex: 30/02 existente?)")

        for campo in self.datas_abreviadas:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        str_valor = str(valor).strip()
                        if not re.match(r'^\d{4}-\d{2}$', str_valor):
                            self._registrar_erro(idx, f"{campo}: Formato inválido. Use AAAA-MM.")
                        else:
                            try:
                                pd.to_datetime(str_valor + "-01", format='%Y-%m-%d', errors='raise')
                            except ValueError:
                                self._registrar_erro(idx, f"{campo}: Mês inválido (ex: 00 ou 13).")

        for campo in self.datas_abreviadas:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor) and not re.match(r'^\d{4}-\d{2}$', str(valor)):
                        self._registrar_erro(idx, f"{campo}: Formato de data abreviada inválido, é esperado AAAA-MM.")

    def validar_campos_obrigatorios(self):
        """Verifica se os campos obrigatórios estão preenchidos"""
        if not self.campos_obrigatorios:
            return
            
        for campo in self.campos_obrigatorios:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.isna(valor) or (isinstance(valor, str) and not valor.strip()):
                        self._registrar_erro(idx, f"{campo}: Campo obrigatório não preenchido.\n")
            else:
                st.error(f"Campo obrigatório '{campo}' não encontrado no arquivo.")
                st.stop()

    def validar_tamanho_campos(self):
        if not self.limites_tamanho:
            return
            
        for campo, tamanho_max in self.limites_tamanho.items():
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor) and len(str(valor)) > tamanho_max:
                        self._registrar_erro(idx, f"{campo}: Tamanho máximo excedido, (max {tamanho_max} caracteres).")

    def validar_valores_monetarios(self):
        self.campos_monetarios = getattr(self, 'campos_monetarios', [])
        if not self.campos_monetarios:
            return
            
        for campo in self.campos_monetarios:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        try:
                            if campo == 'PREC_UNIT':
                                if not verificar_formato_brasileiro(valor, 4):
                                    self._registrar_erro(idx,
                                                         f"{campo}: Formato monetário inválido (use 4 casas decimais), ex: 1.234,5600 ou 1234,5600 ou 123.")
                            else:
                                if not verificar_formato_brasileiro(valor, 2):
                                    self._registrar_erro(idx,
                                                         f"{campo}: Formato monetário inválido, use 1.234,56 ou 1234,56 ou 123.")
                        except (ValueError, TypeError):
                            self._registrar_erro(idx, f"{campo}: Valor monetário inválido.")
                            
        # Valida se são positivos
        for campo in self.campos_monetarios:
            if campo in self.df.columns:
                if campo in getattr(self, 'campos_negativos', []):
                    continue
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        try:
                            if isinstance(valor, str):
                                valor_convertido = valor.replace(".", "").replace(",", ".")
                            else:
                                valor_convertido = str(valor).replace(",", ".")

                            valor_num = float(valor_convertido)

                            if valor_num < 0:
                                self._registrar_erro(idx, f"{campo}: Não pode ser negativo.")

                        except (ValueError, TypeError):
                            pass  # Ignora erros de conversão para validação de positivo

    def validar_numeros_com_decimais(self):
        """Valida se os campos configurados contêm números com até duas casas decimais (formato brasileiro)"""
        self.numeros_com_decimais = getattr(self, 'numeros_com_decimais', [])

        for campo in self.numeros_com_decimais:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        valor_str = str(valor).strip()

                        # Remove qualquer espaço em branco
                        valor_str = valor_str.replace(" ", "")

                        # Verifica se tem formato válido (número com até duas casas decimais)
                        if not re.fullmatch(r'^-?\d+(,\d{0,2})?$', valor_str):
                            self._registrar_erro(idx,
                                                 f"{campo}: Formato numérico inválido. Use vírgula para decimais (ex: 1234,56 ou 123,00 ou 45)")
                            continue

                        # Verifica se tem vírgula mas não tem dígitos após
                        if valor_str.endswith(','):
                            self._registrar_erro(idx,
                                                 f"{campo}: Formato incompleto. Após vírgula deve ter 1 ou 2 dígitos (ex: 123,00)")

        # Valida se são positivos
        for campo in self.numeros_com_decimais:
            if campo in self.df.columns:
                if campo in getattr(self, 'campos_negativos', []):
                    continue
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        try:
                            if isinstance(valor, str):
                                valor_convertido = valor.replace(".", "").replace(",", ".")
                            else:
                                valor_convertido = str(valor).replace(",", ".")

                            valor_num = float(valor_convertido)

                            if valor_num < 0:
                                self._registrar_erro(idx, f"{campo}: Não pode ser negativo.")

                        except (ValueError, TypeError):
                            pass  # Ignora erros de conversão para validação de positivo

    def validar_tipo_de_vinculo(self):
        if not hasattr(self, 'tipos_de_vinculo') or not self.tipos_de_vinculo:
            return
            
        campos = ['TIPO_VINCULO', 'VINCULACAO']
        for campo in campos:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        try:
                            if str(valor) not in self.tipos_de_vinculo:
                                self._registrar_erro(idx, f"{campo}: Não encontrado na lista de vínculos válidos.")
                        except Exception as e:
                            self._registrar_erro(idx, f"{campo}: Erro na validação - {str(e)}")

    def validar_inteiros(self):
        """Valida se os campos configurados contêm valores inteiros"""
        self.campos_inteiros = getattr(self, 'campos_inteiros', [])
        if not self.campos_inteiros:
            return
            
        for campo in self.campos_inteiros:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        try:
                            int(valor)
                            if isinstance(valor, float) and not valor.is_integer():
                                raise ValueError
                        except (ValueError, TypeError):
                            self._registrar_erro(idx, f"{campo}: Deve ser um número inteiro válido.")
                            continue
                            
                        try:
                            if isinstance(valor, str):
                                valor_convertido = valor.replace(".", "").replace(",", ".")
                            else:
                                valor_convertido = str(valor).replace(",", ".")

                            valor_num = float(valor_convertido)

                            if valor_num < 0:
                                self._registrar_erro(idx, f"{campo}: Não pode ser negativo.")

                        except (ValueError, TypeError):
                            pass

    def validar_positivo(self, campos):
        """Valida se os campos fornecidos contêm valores não negativos, exceto os em campos_negativos."""
        campos_negativos = getattr(self, 'campos_negativos', [])
        for campo in campos:
            if campo in self.df.columns:
                if campo in campos_negativos:
                    continue
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        try:
                            if isinstance(valor, str):
                                valor_convertido = valor.replace(".", "").replace(",", ".")
                            else:
                                valor_convertido = str(valor).replace(",", ".")

                            valor_num = float(valor_convertido)

                            if valor_num < 0:
                                self._registrar_erro(idx, f"{campo}: Não pode ser negativo.")

                        except (ValueError, TypeError):
                            self._registrar_erro(idx, f"{campo}: Valor numérico inválido.")

    def validar_cpf(self):
        self.campos_cpf = getattr(self, 'campos_cpf', [])
        if not self.campos_cpf:
            return
            
        for campo in self.campos_cpf:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        try:
                            valor_split = str(valor).split(' ')[0]
                            if valida_cpf(valor_split) == False:
                                self._registrar_erro(idx, f"{campo}: CPF inválido.")
                        except Exception as e:
                            self._registrar_erro(idx, f"{campo}: Erro na validação - {str(e)}")

    def validar_cnpj(self):
        self.campos_cnpj = getattr(self, 'campos_cnpj', [])
        if not self.campos_cnpj:
            return
            
        for campo in self.campos_cnpj:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        try:
                            valor_split = str(valor).split(' ')[0]
                            if valida_cnpj(valor_split) == False:
                                self._registrar_erro(idx, f"{campo}: CNPJ inválido.")
                        except Exception as e:
                            self._registrar_erro(idx, f"{campo}: Erro na validação - {str(e)}")

    def validar_nome(self):
        self.campos_nome = getattr(self, 'campos_nome', [])
        if not self.campos_nome:
            return
            
        for campo in self.campos_nome:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        validacoes = []
                        if not isinstance(valor, str):
                            validacoes.append(f"{campo}: Deve ser texto.")
                        else:
                            valor_clean = valor.strip()
                            if len(valor_clean) > 100:
                                validacoes.append(f"{campo}: Máximo 100 caracteres.")
                            if not re.fullmatch(r'[a-zA-Z0-9\sà-üÀ-ÜçÇéÉãÃõÕôÔîÎûÛ]+', valor_clean):
                                validacoes.append(f"{campo}: Caracteres inválidos.")

                        if validacoes:
                            self._registrar_erro(idx, "\n".join(validacoes))

    def validar_tipo_fornecedor(self):
        self.campo_tipo_fornecedor = ['TIPO']
        campo_documento = 'CNPJ_CPF'

        for campo in self.campo_tipo_fornecedor:
            if campo in self.df.columns and campo_documento in self.df.columns:
                for idx, row in self.df.iterrows():
                    tipo = row[campo]
                    documento = row[campo_documento]
                    validacoes = []

                    if pd.isna(tipo):
                        validacoes.append(f"{campo}: Campo obrigatório não preenchido.")
                    else:
                        tipo_clean = str(tipo).strip().upper()
                        if tipo_clean not in ['J', 'F']:
                            validacoes.append(f"{campo}: Valor inválido. Deve ser 'J' (Jurídica) ou 'F' (Física).")
                        else:
                            if pd.isna(documento) or str(documento).strip() == '':
                                validacoes.append(f"{campo_documento}: Campo obrigatório não preenchido.")
                            else:
                                doc_str = str(documento).strip()
                                if tipo_clean == 'J':
                                    if valida_cnpj(doc_str) == False:
                                        validacoes.append(f"{campo_documento}: CNPJ inválido.")
                                elif tipo_clean == 'F':
                                    if valida_cpf(doc_str) == False:
                                        validacoes.append(f"{campo_documento}: CPF inválido.")

                    if validacoes:
                        self._registrar_erro(idx, "\n".join(validacoes))

    def validar_email(self):
        self.campos_email = getattr(self, 'campos_email', [])
        if not self.campos_email:
            return
            
        for campo in self.campos_email:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        validacoes = []
                        if not isinstance(valor, str):
                            validacoes.append(f"{campo}: Deve ser texto.")
                        else:
                            valor_clean = valor.strip()
                            if not re.fullmatch(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', valor_clean):
                                validacoes.append(f"{campo}: Formato de e-mail inválido.")

                        if validacoes:
                            self._registrar_erro(idx, "\n".join(validacoes))

    def validar_razao_social(self):
        self.campos_razao_social = getattr(self, 'campos_razao_social', [])
        if not self.campos_razao_social:
            return
            
        for campo in self.campos_razao_social:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        validacoes = []
                        if not isinstance(valor, str):
                            validacoes.append(f"{campo}: Deve ser texto.")
                        else:
                            valor_clean = valor.strip()
                            if len(valor_clean) > 100:
                                validacoes.append(f"{campo}: Máximo 100 caracteres.")
                            if not re.fullmatch(r'[a-zA-Z0-9\sà-üÀ-ÜçÇéÉãÃõÕôÔîÎûÛ\.,\-_&/\()\?%]+', valor_clean):
                                validacoes.append(f"{campo}: Caracteres inválidos.")

                        if validacoes:
                            self._registrar_erro(idx, "\n".join(validacoes))

    def validar_contrato(self):
        self.campo_contrato = getattr(self, 'campo_contrato', [])
        if not self.campo_contrato:
            return
            
        for campo in self.campo_contrato:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        if not validar_formato_contrato(str(valor)):
                            self._registrar_erro(idx, f"{campo}: Formato inválido. Use XXXX/XXXX ou XXXX/XXX-TC.")

    def validar_documentos_pdf(self):
        """Valida colunas que contêm nomes de arquivos PDF"""
        self.campos_pdf = getattr(self, 'campos_pdf', [])
        if not self.campos_pdf:
            return
            
        for campo in self.campos_pdf:
            if campo in self.df.columns:
                for idx, valor in self.df[campo].items():
                    if pd.notna(valor):
                        validacoes = []
                        valor = str(valor).strip()

                        if not isinstance(self.df.at[idx, campo], str):
                            validacoes.append(f'{campo}: Deve ser uma string.')

                        if not valor.lower().endswith('.pdf'):
                            validacoes.append(f'{campo}: Deve terminar com .pdf.')
                        else:
                            if not valor.endswith('.pdf'):
                                validacoes.append(f'{campo}: Extensão .pdf deve ser minúscula.')

                        if len(valor) > 150:
                            validacoes.append(f'{campo}: Tamanho máximo excedido (150 caracteres).')

                        nome_base = valor[:-4] if valor.lower().endswith('.pdf') else valor
                        if not re.fullmatch(r'^[A-Z0-9_]+$', nome_base):
                            validacoes.append(f'{campo}: Deve conter apenas letras maiúsculas, números e underline (_).')

                        if validacoes:
                            self._registrar_erro(idx, '\n'.join(validacoes))

    def validar_coluna_d(self):
        if 'D' in self.df.columns:
            for idx, valor in self.df['D'].items():
                if pd.notna(valor):
                    if valor != 'D':
                        self._registrar_erro(idx, "Coluna D deve conter apenas o valor 'D'.")

    def validar_cabecalho(self):
        if not self.cabecalho or not self.campos_obrigatorios:
            return
            
        uploaded_columns = [col.strip().replace(" ", "").upper() for col in self.df.columns.tolist()]
        expected_columns = [col.strip().replace(" ", "").upper() for col in self.cabecalho]

        # Verificar campos obrigatórios faltantes
        missing_required_columns = []
        for required_col in [col.strip().replace(" ", "").upper() for col in self.campos_obrigatorios]:
            if required_col not in uploaded_columns:
                missing_required_columns.append(required_col)

        if missing_required_columns:
            st.error(f"❌ Colunas obrigatórias faltantes: {', '.join(missing_required_columns)}")

        # Verificar se todos os campos do cabeçalho esperado estão presentes
        missing_all_columns = []
        for expected_col in expected_columns:
            if expected_col not in uploaded_columns:
                missing_all_columns.append(expected_col)

        if missing_all_columns:
            st.error(f"❌ Colunas faltantes no arquivo: {', '.join(missing_all_columns)}")

        # Verificar colunas extras
        extra_columns = [col for col in uploaded_columns if col not in expected_columns]
        if extra_columns:
            st.warning(f"⚠️ Colunas extras/não reconhecidas: {', '.join(extra_columns)}")

        if missing_required_columns or missing_all_columns or extra_columns:
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
            st.toast("Coluna ANO_MES_REF não encontrada", icon="⚠️")
            st.stop()

        if 'VALIDACAO' not in self.df.columns:
            self.df['VALIDACAO'] = ''

        if len(self.df['ANO_MES_REF'].unique()) > 1:
            st.error("Múltiplos períodos de referência na coluna ANO_MES_REF")
            st.toast("Múltiplos períodos de referência na coluna ANO_MES_REF", icon="⚠️")
            self.df['VALIDACAO'] = self.df['VALIDACAO'].apply(
                lambda x: x + ', ' if x else '') + 'MÚLTIPLOS PERÍODOS DE REFERÊNCIA NA COLUNA ANO_MES_REF'
            st.stop()

        if not all(self.df['ANO_MES_REF'].astype(str).str.match(r'^\d{4}-\d{2}$')):
            st.error("Formato inválido para ANO_MES_REF (deve ser AAAA-MM)")
            st.toast("Formato inválido para ANO_MES_REF (deve ser AAAA-MM)", icon="⚠️")
            self.df['VALIDACAO'] = self.df['VALIDACAO'].apply(
                lambda x: x + ', ' if x else '') + 'FORMATO INVÁLIDO PARA ANO_MES_REF (DEVE SER AAAA-MM)'
            st.stop()

    def check_id(self):
        if 'ID' not in self.df.columns:
            st.error("Coluna ID não encontrada")
            st.toast("Coluna ID não encontrada", icon="⚠️")
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
            st.toast(f"Módulo '{modulo}' não é suportado", icon="⚠️")
            st.stop()

        valid_attributes = self.valid_attributes

        mask = ~self.df['ATRIBUTO'].isin(valid_attributes)
        atributos_invalidos = self.df[mask]['ATRIBUTO'].unique()

        if len(atributos_invalidos) > 0:

            self.df.loc[mask, 'VALIDACAO'] = self.df.loc[mask, 'VALIDACAO'].apply(
                lambda x: x + ', ' if x else '') + f'ATRIBUTO NÃO RECONHECIDO PARA O MÓDULO DE {modulo} (OS ATRIBUTOS VÁLIDOS SÃO: {", ".join(valid_attributes)})'

    def check_duplicatas_por_id_atributo(self):
        """Verifica se há duplicatas de (ID, ATRIBUTO) no DataFrame."""
        if 'VALIDACAO' not in self.df.columns:
            self.df['VALIDACAO'] = ''

        duplicatas = self.df.duplicated(subset=['ID', 'ATRIBUTO'], keep=False)
        if duplicatas.any():
            grupos = self.df.groupby(['ID', 'ATRIBUTO']).size().reset_index(name='count')
            grupos_duplicatas = grupos[grupos['count'] > 1]

            for _, grupo in grupos_duplicatas.iterrows():
                id_dup = grupo['ID']
                atributo_dup = grupo['ATRIBUTO']
                count = grupo['count']

                indices = self.df[(self.df['ID'] == id_dup) & (self.df['ATRIBUTO'] == atributo_dup)].index
                for idx in indices:
                    self.preencher_validacao(idx, [
                        f"DUPLICATA ENCONTRADA PARA O MESMO ID E ATRIBUTO. EXISTEM {count} REGISTROS PARA ALTERAR O MESMO ATRIBUTO DO MESMO ID."])

    def preencher_validacao(self, idx, validacoes):
        validacao_existente = self.df.at[idx, 'VALIDACAO'] if 'VALIDACAO' in self.df.columns and pd.notna(
            self.df.at[idx, 'VALIDACAO']) else ''

        novas_validacoes = '\n'.join(validacoes) if validacoes else ''

        if validacao_existente or novas_validacoes:
            self.df.at[idx, 'VALIDACAO'] = '\n'.join(filter(None, [validacao_existente, novas_validacoes]))
        else:
            self.df.at[idx, 'VALIDACAO'] = 'OK'

    @abstractmethod
    def validar_alteracao(self):
        pass

    def validar_exclusao(self):
        """Valida se as colunas ATRIBUTO e NOVO_VALOR contêm 'EXCLUSAO' para operações de exclusão."""
        if 'VALIDACAO' not in self.df.columns:
            self.df['VALIDACAO'] = ''

        for idx, row in self.df.iterrows():
            atributo = row['ATRIBUTO']
            novo_valor = row['NOVO_VALOR']

            atributo_str = str(atributo).strip().upper() if pd.notna(atributo) else ''
            novo_valor_str = str(novo_valor).strip().upper() if pd.notna(novo_valor) else ''

            if atributo_str == 'EXCLUSAO' and novo_valor_str == 'EXCLUSAO':
                self.preencher_validacao(idx, [])
            else:
                self.preencher_validacao(idx, ["ATRIBUTO e NOVO_VALOR devem ser 'EXCLUSAO' para ACAO de EXCLUSAO."])
        return self.df