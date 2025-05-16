from models.base_validador import BaseValidator
from models.common import LISTA_ATRIBUTOS_RECEITAS
import re
import pandas as pd
from utils.utils import erros, obter_contratos
from utils.tratamentos import limpar_dados, padronizar_texto, verificar_formato_brasileiro, string_to_float
from models.registry import RegistryValidators

class ReceitasValidator(BaseValidator):
    def __init__(self, df, tipo_de_acao):
        super().__init__(df, tipo_de_acao)
        self.valid_attributes = LISTA_ATRIBUTOS_RECEITAS

    def validar_alteracao(self):

        for id, grupo in self.df.groupby('ID'):
            for idx, row in grupo.iterrows():
                validacoes = []
                attr = row['ATRIBUTO']
                valor = row['NOVO_VALOR']

                if pd.isna(valor) or valor is None or str(valor).strip() == '':
                    self.df.at[idx, 'VALIDACAO'] = 'OK'
                    continue

                if isinstance(valor, str):
                    if not verificar_formato_brasileiro(valor):
                        validacoes.append('FORMATO INVÁLIDO (USE . PARA MILHARES E , DECIMAL COM 2 CASAS)')
                        self.df.at[idx, 'VALIDACAO'] = ', '.join(validacoes)
                        continue

                    try:
                        valor = float(string_to_float(str(valor)))
                    except ValueError:
                        validacoes.append('VALOR INVÁLIDO (NÃO NUMÉRICO)')
                        self.df.at[idx, 'VALIDACAO'] = ', '.join(validacoes)
                        continue

                if attr != 'RESULTADO DE APLICACAO FINANCEIRA' and float(valor) < 0:
                    validacoes.append('VALOR NÃO PODE SER NEGATIVO')

                self.preencher_validacao(idx, validacoes)
        return self.df

RegistryValidators.register_alt_exc('Receitas', ReceitasValidator)