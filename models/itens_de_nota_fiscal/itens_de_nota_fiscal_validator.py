from models.validators.base_validator import BaseValidator
from models.common import LISTA_ATRIBUTOS_ITENS_DE_NOTA_FISCAL
import re
import pandas as pd
from utils.tratamentos import string_to_float
from utils.utils import erros, obter_contratos
from utils.tratamentos import limpar_dados, padronizar_texto
from utils.tratamentos import string_to_float, formata_cnpj

class ItensDeNotaFiscalValidator(BaseValidator):
    def __init__(self, df, tipo_de_acao):
        super().__init__(df, tipo_de_acao)
        self.valid_attributes = LISTA_ATRIBUTOS_ITENS_DE_NOTA_FISCAL

    def validate_data(self):
        self.df['VALIDACAO'] = ''

        for id, grupo in self.df.groupby('ID'):
            atributos = grupo.set_index('ATRIBUTO')['NOVO_VALOR'].to_dict()
            atributos = {k: (None if pd.isna(v) else v) for k, v in atributos.items()}
            for idx, row in grupo.iterrows():
                validacoes = []
                attr = row['ATRIBUTO']
                valor = row['NOVO_VALOR']
                if attr in ['CODIGO DO SERVICO', 'CODIGO DO MATERIAL']:
                    if atributos.get('CODIGO DO SERVICO') and atributos.get('CODIGO DO MATERIAL'):
                        validacoes.append('Dados de serviço e material (um deles precisa estar vazio para realizarmos a troca), ')
                if attr in ['NUMERO DA NOTA FISCAL', 'CODIGO DO SERVICO', 'CODIGO DO MATERIAL',
                            'QUANTIDADE']:
                    if isinstance(valor, str):
                        try:
                            valor = int(valor)
                        except ValueError:
                            validacoes.append('VALOR INVÁLIDO (NÃO NUMÉRICO), ')
                            valor = None
                    if isinstance(valor, int) and valor < 0:
                        validacoes.append('VALOR NÃO PODE SER NEGATIVO, ')
                if attr in ['FORNECEDOR']:
                    if (atributos.get('FORNECEDOR')):
                        valor_split = atributos.get('FORNECEDOR').split(' ')[0]
                        if formata_cnpj(valor_split) == 'invalido':
                            validacoes.append('FORNECEDOR INVALIDO, ')
                if attr in ['VALOR UNITARIO', 'VALOR TOTAL']:
                    if isinstance(valor, str):
                        try:
                            valor = float(string_to_float(str(valor)))
                        except ValueError:
                            validacoes.append('VALOR INVÁLIDO (NÃO NUMÉRICO), ')
                    if isinstance(valor, float) and valor < 0:
                        validacoes.append('VALOR NÃO PODE SER NEGATIVO, ')

                self.df.at[idx, 'VALIDACAO'] = ', '.join(validacoes) if validacoes else 'OK'

        return self.df