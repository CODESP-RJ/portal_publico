from models.validators.base_validator import BaseValidatorIns
from models.registry import RegistryValidators
import datetime
from models.common import CONFIGURACOES_MODULOS
import pandas as pd
from utils.utils import obter_tipos_rubricas, obter_tipos_despesas, obter_tipos_documentos, obter_contas_bancarias

class DespesasValidator(BaseValidatorIns):
    def __init__(self, df):
        super().__init__(df)
        self.config = CONFIGURACOES_MODULOS['modulo_despesas']
        self.cabecalho_str = self.config['cabecalho_str']
        self.cabecalho = self.trata_cabecalho(self.cabecalho_str)
        self.datas_abreviadas = self.config['datas_abreviadas']
        self.datas_completas = self.config['datas_completas']
        self.campos_obrigatorios = self.config['campos_obrigatorios']
        self.campos_monetarios = self.config['campos_monetarios']
        self.limites_tamanho = self.config['limites_tamanho']

        self.campos_pdf = ['DESCRICAO']
        self.campos_cpf = ['CPF']
        self.campos_cnpj = ['CNPJ']
        self.campos_razao_social = ['RAZAO']
        self.campos_nome = ['NOME']
        self.campos_inteiros = ['COD_OS', 'COD_UNIDADE', 'CODIGO', 'NUM_DOCUMENTO', 'RUBRICA', 'BANCO', 'AGENCIA', 'PMT_PAGA', 'QTDE_PMT']
        self.rubricas_validas = [str(r["id_rubrica"]) for r in obter_tipos_rubricas()]
        self.contas_validas = self._gerar_lista_contas()
        self.tipos_despesa_validos = [str(t["cod_despesa"]) for t in obter_tipos_despesas()]
        self.tipos_documento_validos = [str(d["cod_tipo_documento"]) for d in obter_tipos_documentos()]

    def _gerar_lista_contas(self):
        return [f"{conta['CODIGO_CC']}{conta['DIGITO_CC']}" for conta in obter_contas_bancarias()]

    def validar_rubrica(self):
        if 'RUBRICA' in self.df.columns:
            for idx, valor in self.df['RUBRICA'].items():
                if pd.notna(valor) and str(valor) not in self.rubricas_validas:
                    self._registrar_erro(idx, "RUBRICA: Código não encontrado na lista de rubricas válidas")

    def validar_conta_corrente(self):
        if 'CONTA_CORRENTE' in self.df.columns:
            for idx, valor in self.df['CONTA_CORRENTE'].items():
                if pd.notna(valor) and str(valor) not in self.contas_validas:
                    self._registrar_erro(idx, "CONTA_CORRENTE: Conta bancária não cadastrada")

    def validar_tipo_de_despesa(self):
        if 'DESPESA' in self.df.columns:
            for idx, valor in self.df['DESPESA'].items():
                if pd.notna(valor) and str(valor) not in self.tipos_despesa_validos:
                    self._registrar_erro(idx, "DESPESA: Código não encontrado na lista de tipos válidos")

    def validar_tipo_de_documento(self):
        if 'TIPO' in self.df.columns:
            for idx, valor in self.df['TIPO'].items():
                if pd.notna(valor):
                    if str(valor) not in self.tipos_documento_validos:
                        self._registrar_erro(idx, "TIPO: Código não encontrado na lista de tipos válidos")
                    elif str(valor) == 'NF':
                        self._validar_campos_nf(idx)

    def _validar_campos_nf(self, idx):
        campos_necessarios = ['SERIE', 'NUM_DOCUMENTO', 'CODIGO']
        faltantes = []

        for campo in campos_necessarios:
            if campo not in self.df.columns or pd.isna(self.df.at[idx, campo]):
                faltantes.append(campo)

        if faltantes:
            self._registrar_erro(idx,
                                 f"TIPO: Colunas obrigatórias faltantes se for o TIPO for NF: {', '.join(faltantes)}")

    def validar_especifico(self):
        self.validar_valores_monetarios()
        self.validar_tamanho_campos()
        self.validar_datas()
        self.validar_documentos_pdf()
        self.validar_rubrica()
        self.validar_conta_corrente()
        self.validar_tipo_de_despesa()
        self.validar_tipo_de_documento()
        self.validar_cpf()
        self.validar_cnpj()
        self.validar_razao_social()
        self.validar_nome()

RegistryValidators.register_ins('modulo_despesas', DespesasValidator)