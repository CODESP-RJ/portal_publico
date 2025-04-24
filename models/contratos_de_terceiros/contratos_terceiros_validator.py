from models.validators.base_validator import BaseValidator
from models.common import LISTA_ATRIBUTOS_CONTRATOS_DE_TERCEIROS
import re
import pandas as pd
from utils.tratamentos import string_to_float, formata_cpf, formata_cnpj
from utils.utils import erros, obter_contratos

class ContratosTerceirosValidator(BaseValidator):
    def __init__(self, df, tipo_de_acao):
        super().__init__(df, tipo_de_acao)
        self.valid_attributes = LISTA_ATRIBUTOS_CONTRATOS_DE_TERCEIROS

    def validate_data(self):
        self.df['VALIDACAO'] = ''

        for id, grupo in self.df.groupby('ID'):
            atributos = grupo.set_index('ATRIBUTO')['NOVO_VALOR'].to_dict()
            atributos = {k: (None if pd.isna(v) else v) for k, v in atributos.items()}
            for idx, row in grupo.iterrows():
                validacoes = []
                attr = row['ATRIBUTO']
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

                if attr in ['ANO INICIO', 'ANO FIM']:
                    if atributos.get('ANO INICIO') > atributos.get('ANO FIM'):
                        validacoes.append('ANO DE INÍCIO MAIOR QUE ANO DE FIM, ')
                if attr in ['MES INICIO', 'ANO INICIO', 'MES FIM', 'ANO FIM', 'VIGENCIA']:
                    valor_split = atributos.get('VIGENCIA').split(' ')
                    try:
                        valor_int = int(valor_split[0])
                        if valor_int < 0:
                            validacoes.append(f'{attr.upper()} NÃO PODE SER NEGATIVO, ')
                        if 'MES' in attr and (valor_int > 12 or valor_int < 1):
                            validacoes.append(f'{attr.upper()} DEVE SER ENTRE 1 E 12, ')
                    except ValueError:
                        validacoes.append(f'{atributo.upper()} NÃO É UM NÚMERO VÁLIDO, ')

                if attr in ['CONTRATO'] and attr not in ['UNIDADE']:
                    req = obter_contratos()
                    if not any(item == atributos.get('CONTRATO') for item in req):
                        validacoes.append('CONTRATO NAO ENCONTRADO NÃO ENCONTRADO, ')

                self.df.at[idx, 'VALIDACAO'] = ', '.join(validacoes) if validacoes else 'OK'

        return self.df