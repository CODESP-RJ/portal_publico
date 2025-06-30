from models.base_validador import BaseValidatorIns
from models.registry import RegistryValidators
import datetime
from models.common import CONFIGURACOES_MODULOS
import pandas as pd

class FornecedoresValidator(BaseValidatorIns):
    def __init__(self, df):
        super().__init__(df)
        self.config = CONFIGURACOES_MODULOS['modulo_fornecedores']
        self.cabecalho_str = self.config['cabecalho_str']
        self.cabecalho = self.trata_cabecalho(self.cabecalho_str)
        self.datas_abreviadas = self.config['datas_abreviadas']
        self.datas_completas = self.config['datas_completas']
        self.campos_obrigatorios = self.config['campos_obrigatorios']
        self.campos_monetarios = self.config['campos_monetarios']
        self.limites_tamanho = self.config['limites_tamanho']

        self.campo_tipo_fornecedor = ['TIPO']
        self.campos_email = ['EMAIL']
        self.campos_inteiros = ['NUMERO']

    def validar_especifico(self):
        self.validar_inteiros()
        self.validar_tamanho_campos()
        self.validar_email()
        self.validar_tipo_fornecedor()

RegistryValidators.register_ins('modulo_fornecedores', FornecedoresValidator)