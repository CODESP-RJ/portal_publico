from models.base_validador import BaseValidatorIns
from models.registry import RegistryValidators
import datetime
from models.common import CONFIGURACOES_MODULOS
import pandas as pd
from utils.utils import obter_tipos_de_vinculo

class ProvisionamentoValidator(BaseValidatorIns):
    def __init__(self, df):
        super().__init__(df)
        self.config = CONFIGURACOES_MODULOS['modulo_provisionamento']
        self.cabecalho_str = self.config['cabecalho_str']
        self.cabecalho = self.trata_cabecalho(self.cabecalho_str)
        self.datas_abreviadas = self.config['datas_abreviadas']
        self.datas_completas = self.config['datas_completas']
        self.campos_obrigatorios = self.config['campos_obrigatorios']
        self.campos_monetarios = self.config['campos_monetarios']
        self.limites_tamanho = self.config['limites_tamanho']

        self.campo_contrato = ['CONTRATO']
        self.campos_cnpj = ['CNPJ']
        self.campos_cpf = ['CPF']
        self.campos_inteiros = ['COD_OS', 'COD_UNIDADE']
        self.numeros_com_decimais = ['PERC_RATEIO', 'CARGA_HORARIA']
        self.tipos_de_vinculo = [str(d["tpvc_cd_tipo_vinculacao"]) for d in obter_tipos_de_vinculo()]

    def validar_tipo_de_vinculo(self):
        if 'TIPO_VINCULO' in self.df.columns:
            for idx, valor in self.df['TIPO_VINCULO'].items():
                if pd.notna(valor):
                    if str(valor) not in self.tipos_de_vinculo:
                        self._registrar_erro(idx, "TIPO_VINCULO: Não encontrado na lista de vínculos válidos.")

    def validar_especifico(self):
        self.validar_inteiros()
        self.validar_datas()
        self.validar_tamanho_campos()
        self.validar_valores_monetarios()
        self.validar_contrato()
        self.validar_cpf()
        self.validar_cnpj()
        self.validar_tipo_de_vinculo()
        self.validar_numeros_com_decimais()

RegistryValidators.register_ins('modulo_provisionamento', ProvisionamentoValidator)