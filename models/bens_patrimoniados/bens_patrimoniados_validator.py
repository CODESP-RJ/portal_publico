from models.validators.base_validator import BaseValidator
from models.common import LISTA_ATRIBUTOS_BENS_PATRIMONIADOS
import re
import pandas as pd
from utils.tratamentos import string_to_float, formata_cpf, formata_cnpj
from utils.utils import erros, obter_contratos, obter_tipos_bens
from utils.tratamentos import limpar_dados, padronizar_texto

class BensPatrimoniadosValidator(BaseValidator):
    def __init__(self, df, tipo_de_acao):
        super().__init__(df, tipo_de_acao)
        self.required_columns = ['TIPO_MODULO', 'ANO_MES_REF', 'ACAO', 'ID', 'ATRIBUTO', 'NOVO_VALOR']
        self.valid_attributes = LISTA_ATRIBUTOS_BENS_PATRIMONIADOS

    def validate_data(self):
        self.df['VALIDACAO'] = ''

        for id, grupo in self.df.groupby('ID'):
            atributos = grupo.set_index('ATRIBUTO')['NOVO_VALOR'].to_dict()
            atributos = {k: (None if pd.isna(v) else v) for k, v in atributos.items()}
            for idx, row in grupo.iterrows():
                validacoes = []
                attr = row['ATRIBUTO']
                valor = row['NOVO_VALOR']
                if attr in ['VIDA UTIL', 'CONTROLE', 'NOTA FISCAL', 'QUANTIDADE', 'TIPO']:
                    if isinstance(valor, str):
                        try:
                            valor = int(valor)
                        except ValueError:
                            validacoes.append('VALOR INVÁLIDO (NÃO NUMÉRICO), ')
                            valor = None
                    if isinstance(valor, int) and valor < 0:
                        validacoes.append('VALOR NÃO PODE SER NEGATIVO, ')

                if attr in ['CNPJ', 'RAZAO SOCIAL']:
                    if (atributos.get('CNPJ')):
                        valor_split = atributos.get('CNPJ').split(' ')[0]
                        if formata_cnpj(valor_split) == 'invalido':
                            validacoes.append('CNPJ INVALIDO, ')
                        if (atributos.get('RAZAO SOCIAL')):
                            if not isinstance(atributos.get('RAZAO SOCIAL'), str):
                                validacoes.append('RAZAO SOCIAL INVALIDO, ')
                            valor = atributos.get('RAZAO SOCIAL').strip()
                            if len(valor) > 100:
                                validacoes.append('RAZAO SOCIAL MAIOR QUE 100 CARACTERES, ')
                            if not re.fullmatch(r'[a-zA-Z0-9\sà-üÀ-ÜçÇéÉãÃõÕôÔîÎûÛ\.,\-_&/\()\?%]+', valor):
                                validacoes.append('RAZAO SOCIAL CONTEM CARACTERES INVALIDOS, ')

                    if not (atributos.get('CNPJ') or atributos.get('RAZAO SOCIAL')):
                        validacoes.append('Dados incompletos para Pessoa Jurídica, ')
                if attr in ['CONTRATO']:
                    req = obter_contratos()
                    if not any(item == atributos.get('CONTRATO') for item in req):
                        validacoes.append('CONTRATO NAO ENCONTRADO NÃO ENCONTRADO, ')
                if attr in ['TIPO']:
                    req = obter_tipos_bens()
                    encontrou = False
                    for tipos in req:
                        if str(tipos["id_bem_tipo"]) == atributos.get('TIPO'):
                            encontrou = True
                    if encontrou == False:
                        validacoes.append('TIPO DE BEM NÃO EXISTE, ')

                self.df.at[idx, 'VALIDACAO'] = ', '.join(validacoes) if validacoes else 'OK'

        return self.df