from models.validators.base_validator import BaseValidator
from models.common import LISTA_ATRIBUTOS_DESPESAS
import re
import pandas as pd
from utils.tratamentos import string_to_float
from utils.utils import erros, obter_contratos
from utils.tratamentos import limpar_dados, padronizar_texto

class DespesasValidator(BaseValidator):
    def __init__(self, df, tipo_de_acao):
        super().__init__(df, tipo_de_acao)
        self.valid_attributes = LISTA_ATRIBUTOS_DESPESAS

    def validate_data(self):
        self.df['VALIDACAO'] = ''

        for id, grupo in self.df.groupby('ID'):
            atributos = grupo.set_index('ATRIBUTO')['NOVO_VALOR'].to_dict()
            atributos = {k: (None if pd.isna(v) else v) for k, v in atributos.items()}
            for idx, row in grupo.iterrows():
                validacoes = []
                attr = row['ATRIBUTO']

                self.df.at[idx, 'VALIDACAO'] = ', '.join(validacoes) if validacoes else 'OK'

        return self.df