from models.validators.base_validator import BaseValidator
from models.common import LISTA_ATRIBUTOS_DESPESAS
import re
import pandas as pd
from utils.tratamentos import string_to_float
from utils.utils import erros, obter_contratos
from utils.tratamentos import limpar_dados, padronizar_texto, string_to_float, formata_cpf, formata_cnpj

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
                valor = row['NOVO_VALOR']

                if attr in ['CPF', 'NOME', 'CNPJ', 'RAZAO SOCIAL']:
                    if (atributos.get('CPF') or atributos.get('NOME')) and (
                            atributos.get('CNPJ') or atributos.get('RAZAO SOCIAL')):
                        validacoes.append('Dados de pessoa física e jurídica (um deles precisa estar vazio para realizarmos a troca), ')
                if attr in ['CPF', 'NOME']:
                    if (atributos.get('CPF')):
                        valor_split = atributos.get('CPF').split(' ')[0]
                        if formata_cpf(valor_split) == 'invalido':
                            validacoes.append('CPF INVALIDO, ')
                    if (atributos.get('NOME')):
                        if not isinstance(atributos.get('NOME'), str):
                            validacoes.append('NOME INVALIDO, ')
                        valor = atributos.get('NOME').strip()
                        if len(valor) > 100:
                            validacoes.append('NOME MAIOR QUE 100 CARACTERES, ')
                        if not re.fullmatch(r'[a-zA-Z0-9\sà-üÀ-ÜçÇéÉãÃõÕôÔîÎûÛ]+', valor):
                            validacoes.append('NOME CONTEM CARACTERES INVALIDOS, ')
                    if not (atributos.get('CPF') and atributos.get('NOME')):
                        if attr in ['CNPJ', 'RAZAO SOCIAL']:
                            validacoes.append('Dados incompletos para Pessoa Física, ')
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
                    if not (atributos.get('CNPJ') and atributos.get('RAZAO SOCIAL')):
                        if attr in ['CPF', 'NOME']:
                            validacoes.append('Dados incompletos para Pessoa Jurídica, ')

                if attr in ['PARCELA PAGA', 'NUMERO DE PARCELAS', 'UNIDADE', 'RUBRICA', 'NUMERO DO DOCUMENTO']:
                    if isinstance(valor, str):
                        try:
                            valor = int(valor)
                        except ValueError:
                            validacoes.append('VALOR INVÁLIDO (NÃO NUMÉRICO), ')
                            valor = None
                    if isinstance(valor, int) and valor < 0:
                        validacoes.append('VALOR NÃO PODE SER NEGATIVO, ')

                if attr in ['NUMERO DO DOCUMENTO']:
                    if len(valor) > 20:
                        validacoes.append('NUMERO DO DOCUMENTO MAIOR QUE 20 CARACTERES, ')
                if attr in ['SERIE']:
                    if len(valor) > 3:
                        validacoes.append('SERIE MAIOR QUE 3 CARACTERES, ')
                    if not re.fullmatch(r'[a-zA-Z0-9]+', valor):
                        validacoes.append('SERIE CONTEM CARACTERES INVALIDOS, ')
                if attr in ['CODIGO FISCAL']:
                    if len(valor) > 30:
                        validacoes.append('CODIGO FISCAL MAIOR QUE 20 CARACTERES, ')
                if attr in ['IDENTIFICADOR BANCARIO']:
                    if len(valor) > 100:
                        validacoes.append('IDENTIFICADOR BANCÁRIO MAIOR QUE 100 CARACTERES, ')
                    if not re.fullmatch(r'[a-zA-Z0-9]+', valor):
                        validacoes.append('IDENTIFICADOR BANCARIO CONTEM CARACTERES INVALIDOS, ')

                if attr in ['VALOR DO DOCUMENTO', 'VALOR PAGO']:
                    if isinstance(valor, str):
                        try:
                            valor = float(string_to_float(str(valor)))
                        except ValueError:
                            validacoes.append('VALOR INVÁLIDO (NÃO NUMÉRICO), ')
                    if isinstance(valor, float) and valor < 0:
                        validacoes.append('VALOR NÃO PODE SER NEGATIVO, ')

                self.df.at[idx, 'VALIDACAO'] = ', '.join(validacoes) if validacoes else 'OK'

        return self.df