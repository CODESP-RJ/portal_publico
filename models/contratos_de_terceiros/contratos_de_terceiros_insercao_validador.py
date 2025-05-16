from models.base_validador import BaseValidatorIns
from models.registry import RegistryValidators
import datetime
from models.common import CONFIGURACOES_MODULOS
import pandas as pd
from utils.utils import obter_tipos_rubricas, obter_tipos_despesas, obter_tipos_documentos, obter_contas_bancarias

class ContratosDeTerceirosValidator(BaseValidatorIns):
    def __init__(self, df):
        super().__init__(df)
        self.config = CONFIGURACOES_MODULOS['modulo_contratos_de_terceiros']
        self.cabecalho_str = self.config['cabecalho_str']
        self.cabecalho = self.trata_cabecalho(self.cabecalho_str)
        self.datas_abreviadas = self.config['datas_abreviadas']
        self.datas_completas = self.config['datas_completas']
        self.campos_obrigatorios = self.config['campos_obrigatorios']
        self.campos_monetarios = self.config['campos_monetarios']
        self.limites_tamanho = self.config['limites_tamanho']

        self.campos_cnpj = ['CNPJ']
        self.campos_razao_social = ['RAZAO_SOCIAL']
        self.campos_inteiros = ['COD_OS', 'COD_UNIDADE', 'VIGENCIA']
        self.campos_pdf = ['IMG_CONTRATO']

    def validar_especifico(self):
        self.validar_valores_monetarios()
        self.validar_tamanho_campos()
        self.validar_datas()
        self.validar_cnpj()
        self.validar_inteiros()
        self.validar_coluna_d()
        self.validar_documentos_pdf()

RegistryValidators.register_ins('modulo_contratos_de_terceiros', ContratosDeTerceirosValidator)