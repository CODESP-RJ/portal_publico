from models.validators.base_validator import BaseValidator
from models.common import LISTA_ATRIBUTOS_SALDOS
import re
import pandas as pd
from utils.tratamentos import string_to_float
from utils.utils import erros, obter_contratos
from utils.tratamentos import limpar_dados, padronizar_texto

class SaldosValidator(BaseValidator):
    def __init__(self, df, tipo_de_acao):
        super().__init__(df, tipo_de_acao)
        self.required_columns = ['TIPO_MODULO', 'ANO_MES_REF', 'ACAO', 'ID', 'ATRIBUTO', 'NOVO_VALOR']
        self.valid_attributes = LISTA_ATRIBUTOS_SALDOS

    def validate_data(self):
        self.df['VALIDACAO'] = ''

        for id, grupo in self.df.groupby('ID'):
            for idx, row in grupo.iterrows():
                validacoes = []
                attr = row['ATRIBUTO']
                valor = row['NOVO_VALOR']
                if isinstance(valor, str):
                    try:
                        valor = float(string_to_float(str(valor)))
                    except ValueError:
                        validacoes.append('VALOR INVÁLIDO (NÃO NUMÉRICO), ')
                if attr != 'VALOR EM CONTA CORRENTE' and valor < 0:
                    validacoes.append('VALOR NÃO PODE SER NEGATIVO, ')

                self.df.at[idx, 'VALIDACAO'] = ', '.join(validacoes) if validacoes else 'OK'

        return self.df