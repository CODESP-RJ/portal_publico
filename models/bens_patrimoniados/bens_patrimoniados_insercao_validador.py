from models.base_validador import BaseValidatorIns
from models.registry import RegistryValidators
import datetime
from models.common import CONFIGURACOES_MODULOS
import pandas as pd
from utils.utils import obter_tipos_rubricas, obter_tipos_despesas, obter_tipos_documentos, obter_contas_bancarias

class BensPatrimoniadosValidator(BaseValidatorIns):
    def __init__(self, df):
        super().__init__(df)
        self.config = CONFIGURACOES_MODULOS['modulo_bens_patrimoniados']
        self.cabecalho_str = self.config['cabecalho_str']
        self.cabecalho = self.trata_cabecalho(self.cabecalho_str)
        self.datas_abreviadas = self.config['datas_abreviadas']
        self.datas_completas = self.config['datas_completas']
        self.campos_obrigatorios = self.config['campos_obrigatorios']
        self.campos_monetarios = self.config['campos_monetarios']
        self.limites_tamanho = self.config['limites_tamanho']

        self.campos_inteiros = ['COD_OS', 'COD_UNIDADE', 'COD_TIPO', 'VIDA_UTIL']
        self.campos_cnpj = ['CNPJ']
        self.campos_razao_social = ['FORNECEDOR']
        self.campos_pdf = ['IMG_NF']
        self.campos_monetarios = ['VALOR', 'QUANTIDADE']

    def validar_especifico(self):
        self.validar_valores_monetarios()
        self.validar_tamanho_campos()
        self.validar_inteiros()
        self.validar_datas()
        self.validar_cnpj()
        self.validar_razao_social()
        self.validar_documentos_pdf()

    def validar_tipo_bem(self):
        tipos_bem = obter_tipos_rubricas()
        for index, row in self.df.iterrows():
            tipo_bem = row['TIPO_BEM']
            if tipo_bem not in tipos_bem:
                self.adicionar_erro(index, 'TIPO_BEM', f'Tipo de bem inválido: {tipo_bem}')

RegistryValidators.register_ins('modulo_bens_patrimoniados', BensPatrimoniadosValidator)