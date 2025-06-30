from models.base_validador import BaseValidatorIns
from models.registry import RegistryValidators
import datetime
from models.common import CONFIGURACOES_MODULOS
import pandas as pd
from utils.utils import obter_tipos_bens
import re

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

        self.campo_contrato = ['COD_CONTRATO']
        self.campos_inteiros = ['COD_OS', 'COD_UNIDADE', 'COD_TIPO', 'VIDA_UTIL']
        self.campos_cnpj = ['CNPJ']
        self.campos_razao_social = ['FORNECEDOR']
        self.campos_pdf = ['IMG_NF']
        self.campos_monetarios = ['VALOR', 'QUANTIDADE']

    def validar_tipo_bem(self):
        tipos_bem = obter_tipos_bens()
        tipo_descricao_map = {
            int(tipo["id_bem_tipo"]): tipo["assetTypeDescription"].split("-", 1)[1].strip().upper()
            for tipo in tipos_bem
        }

        for idx, row in self.df.iterrows():
            id_tipo_bem = row['COD_TIPO']
            desc_tipo_bem = str(row['BEM_TIPO']).strip().upper() if pd.notnull(row['BEM_TIPO']) else ''

            try:
                id_tipo_bem = int(id_tipo_bem)
            except (ValueError, TypeError):
                self._registrar_erro(idx, f'COD_TIPO: Deve ser um número inteiro válido.')
                continue

            if id_tipo_bem not in tipo_descricao_map:
                self._registrar_erro(idx, f'Tipo de bem inválido: {id_tipo_bem}.')
            else:
                desc_correta = tipo_descricao_map[id_tipo_bem]
                if desc_tipo_bem != desc_correta:
                    self._registrar_erro(idx, f'BEM_TIPO: Incorreto. Esperado: {desc_correta}.')

    def validar_especifico(self):
        self.validar_inteiros()
        self.validar_datas()
        self.validar_tamanho_campos()
        self.validar_valores_monetarios()
        self.validar_contrato()
        self.validar_documentos_pdf()
        self.validar_cnpj()
        self.validar_razao_social()
        self.validar_tipo_bem()

RegistryValidators.register_ins('modulo_bens_patrimoniados', BensPatrimoniadosValidator)
