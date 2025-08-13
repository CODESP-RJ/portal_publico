from models.base_validador import BaseValidatorIns
from models.registry import RegistryValidators
import datetime
from models.common import CONFIGURACOES_MODULOS
import pandas as pd
from utils.utils import obter_tipos_de_vinculo

class FuncionariosValidator(BaseValidatorIns):
    def __init__(self, df):
        super().__init__(df)
        self.config = CONFIGURACOES_MODULOS['modulo_funcionarios']
        self.cabecalho_str = self.config['cabecalho_str']
        self.cabecalho = self.trata_cabecalho(self.cabecalho_str)
        self.datas_abreviadas = self.config['datas_abreviadas']
        self.datas_completas = self.config['datas_completas']
        self.campos_obrigatorios = self.config['campos_obrigatorios']
        self.campos_monetarios = self.config['campos_monetarios']
        self.limites_tamanho = self.config['limites_tamanho']

        self.campos_cpf = ['CPF']
        self.campos_inteiros = ['COD_OS', 'SEXO', 'RACA', 'ESCOLARIDADE', 'COD_PAIS_ORIGEM']
        self.campo_contrato = []

    def validar_especifico(self):
        self.validar_inteiros()
        self.validar_datas()
        self.validar_tamanho_campos()
        self.validar_cpf()

RegistryValidators.register_ins('modulo_funcionarios', FuncionariosValidator)