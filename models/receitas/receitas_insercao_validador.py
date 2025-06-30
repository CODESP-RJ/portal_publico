from models.base_validador import BaseValidatorIns
from models.registry import RegistryValidators
import datetime
from models.common import CONFIGURACOES_MODULOS
import pandas as pd

class ReceitasValidator(BaseValidatorIns):
    def __init__(self, df):
        super().__init__(df)
        self.config = CONFIGURACOES_MODULOS['modulo_receitas']
        self.cabecalho_str = self.config['cabecalho_str']
        self.cabecalho = self.trata_cabecalho(self.cabecalho_str)
        self.datas_abreviadas = self.config['datas_abreviadas']
        self.datas_completas = self.config['datas_completas']
        self.campos_obrigatorios = self.config['campos_obrigatorios']
        self.campos_monetarios = self.config['campos_monetarios']
        self.limites_tamanho = self.config['limites_tamanho']

        self.campo_contrato = ['COD_CONTRATO']
        self.campos_inteiros = ['COD_OS', 'COD_UNIDADE', 'BANCO', 'AGENCIA', 'CONTA_CORRENTE']
        self.campos_negativos = ['REC_APLIC_FINANCEIRA']

    def validar_especifico(self):
        self.validar_coluna_d()
        self.validar_inteiros()
        self.validar_datas()
        self.validar_tamanho_campos()
        self.validar_valores_monetarios()
        self.validar_contrato()

RegistryValidators.register_ins('modulo_receitas', ReceitasValidator)