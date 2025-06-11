from models.base_validador import BaseValidator
from models.common import LISTA_ATRIBUTOS_DESPESAS
import re
import pandas as pd
from utils.tratamentos import string_to_float
from utils.utils import erros, obter_contratos
from utils.tratamentos import limpar_dados, padronizar_texto, string_to_float, formata_cpf, formata_cnpj, verificar_formato_brasileiro, validar_data_brasileira
from utils.utils import obter_tipos_rubricas, obter_tipos_despesas, obter_tipos_documentos, obter_contas_bancarias
from models.registry import RegistryValidators

class DespesasValidator(BaseValidator):
    def __init__(self, df, tipo_de_acao):
        super().__init__(df, tipo_de_acao)
        self.valid_attributes = LISTA_ATRIBUTOS_DESPESAS

    def validar_alteracao(self):

        for id, grupo in self.df.groupby('ID'):
            atributos = grupo.set_index('ATRIBUTO')['NOVO_VALOR'].to_dict()
            atributos = {k: (None if pd.isna(v) else v) for k, v in atributos.items()}
            for idx, row in grupo.iterrows():
                validacoes = []
                attr = row['ATRIBUTO']
                valor = row['NOVO_VALOR']

                if attr in ['CNPJ']:
                    if (atributos.get('CNPJ')):
                        valor_split = atributos.get('CNPJ').split(' ')[0]
                        if formata_cnpj(valor_split) == 'invalido':
                            validacoes.append('CNPJ INVALIDO, ')
                if attr in ['CPF']:
                    if (atributos.get('CPF')):
                        valor_split = atributos.get('CPF').split(' ')[0]
                        if formata_cpf(valor_split) == 'invalido':
                            validacoes.append('CPF INVALIDO, ')
                if attr in ['RAZAO SOCIAL']:
                    if (atributos.get('RAZAO SOCIAL')):
                        if not isinstance(atributos.get('RAZAO SOCIAL'), str):
                            validacoes.append('RAZAO SOCIAL INVALIDO, ')
                        valor = atributos.get('RAZAO SOCIAL').strip()
                        if len(valor) > 100:
                            validacoes.append('RAZAO SOCIAL MAIOR QUE 100 CARACTERES, ')
                        if not re.fullmatch(r'[a-zA-Z0-9\sà-üÀ-ÜçÇéÉãÃõÕôÔîÎûÛ\.,\-_&/\()\?%]+', valor):
                            validacoes.append('RAZAO SOCIAL CONTEM CARACTERES INVALIDOS, ')
                if attr in ['NOME']:
                    if (atributos.get('NOME')):
                        if not isinstance(atributos.get('NOME'), str):
                            validacoes.append('NOME INVALIDO, ')
                        valor = atributos.get('NOME').strip()
                        if len(valor) > 100:
                            validacoes.append('NOME MAIOR QUE 100 CARACTERES, ')
                        if not re.fullmatch(r'[a-zA-Z0-9\sà-üÀ-ÜçÇéÉãÃõÕôÔîÎûÛ]+', valor):
                            validacoes.append('NOME CONTEM CARACTERES INVALIDOS, ')

                if attr in ['CPF', 'NOME', 'CNPJ', 'RAZAO SOCIAL']:
                    if (atributos.get('CPF') or atributos.get('NOME')) and (
                            atributos.get('CNPJ') or atributos.get('RAZAO SOCIAL')):
                        validacoes.append('DADOS DE PESSOA FÍSICA E JURÍDICA (UM DELES PRECISA ESTAR VAZIO PARA REALIZARMOS A TROCA), ')

                if attr in ['CPF', 'NOME']:
                    if not (atributos.get('CPF') and atributos.get('NOME')):
                        if attr in ['CNPJ', 'RAZAO SOCIAL']:
                            validacoes.append('DADOS INCOMPLETOS PARA PESSOA FÍSICA, ')

                if attr in ['CNPJ', 'RAZAO SOCIAL']:
                    if not (atributos.get('CNPJ') and atributos.get('RAZAO SOCIAL')):
                        if attr in ['CPF', 'NOME']:
                            validacoes.append('DADOS INCOMPLETOS PARA PESSOA JURÍDICA, ')

                if attr in ['DESCRICAO']:
                    if not isinstance(valor, str):
                        validacoes.append('DESCRICAO INVALIDA, ')

                    valor = str(valor).strip()

                    # Verifica se termina com .pdf (em minúsculo)
                    if not valor.lower().endswith('.pdf'):
                        validacoes.append('DESCRICAO DEVE TERMINAR COM .pdf, ')
                    else:
                        # Garante que .pdf está em minúsculo
                        if not valor.endswith('.pdf'):
                            validacoes.append('A EXTENSÃO .pdf DEVE SER MINÚSCULA, ')

                    # Remove a extensão .pdf para validar o nome do arquivo
                    nome_arquivo = valor[:-4] if valor.lower().endswith('.pdf') else valor

                    # Verifica o comprimento (considerando os 4 caracteres de .pdf)
                    if len(valor) > 150:
                        validacoes.append('DESCRICAO MAIOR QUE 150 CARACTERES, ')

                    # Verifica se o nome do arquivo (sem .pdf) contém apenas letras, números e underline
                    if not re.fullmatch(r'^[A-Z0-9_]+$', nome_arquivo):
                        validacoes.append('DESCRICAO SÓ PODE CONTER LETRAS MAIÚSCULAS, NÚMEROS E UNDERLINE (_), ')

                if attr in ['PARCELA PAGA', 'NUMERO DE PARCELAS', 'UNIDADE', 'RUBRICA', 'NUMERO DO DOCUMENTO', 'UNIDADE']:
                    if isinstance(valor, str):
                        try:
                            valor = int(valor)
                        except ValueError:
                            validacoes.append('VALOR INVÁLIDO (NÃO NUMÉRICO), ')
                            valor = None
                    if isinstance(valor, int) and valor < 0:
                        validacoes.append('VALOR NÃO PODE SER NEGATIVO, ')

                if attr in ['NUMERO DO DOCUMENTO']:
                    if isinstance(valor, str) and len(valor) > 20:
                        validacoes.append('NUMERO DO DOCUMENTO MAIOR QUE 20 CARACTERES, ')

                if attr in ['SERIE']:
                    if isinstance(valor, str) and len(valor) > 3:
                        validacoes.append('SERIE MAIOR QUE 3 CARACTERES, ')
                    if not re.fullmatch(r'[a-zA-Z0-9]+', valor):
                        validacoes.append('SERIE CONTEM CARACTERES INVALIDOS, ')

                if attr in ['CODIGO FISCAL']:
                    if isinstance(valor, str) and len(valor) > 30:
                        validacoes.append('CODIGO FISCAL MAIOR QUE 20 CARACTERES, ')

                if attr in ['IDENTIFICADOR BANCARIO']:
                    if isinstance(valor, str) and len(valor) > 100:
                        validacoes.append('IDENTIFICADOR BANCÁRIO MAIOR QUE 100 CARACTERES, ')
                    if not re.fullmatch(r'[a-zA-Z0-9]+', valor):
                        validacoes.append('IDENTIFICADOR BANCARIO CONTEM CARACTERES INVALIDOS, ')

                if attr in ['VALOR DO DOCUMENTO', 'VALOR PAGO']:
                    if isinstance(valor, str) and not verificar_formato_brasileiro(valor):
                        validacoes.append('FORMATO INVÁLIDO (USE . PARA MILHARES E , DECIMAL COM 2 CASAS)')
                    try:
                        valor = float(string_to_float(str(valor)))
                    except ValueError:
                        validacoes.append('VALOR INVÁLIDO (NÃO NUMÉRICO), ')
                    if isinstance(valor, float) and valor < 0:
                        validacoes.append('VALOR NÃO PODE SER NEGATIVO, ')

                if attr in ['DATA DE VENCIMENTO', 'DATA DE EMISSAO', 'DATA DE PAGAMENTO', 'DATA DE APURACAO']:
                    if not validar_data_brasileira(valor):
                        validacoes.append(f'{attr} DEVE ESTAR NO FORMATO DD/MM/YYYY, ')

                if attr in ['UNIDADE']:
                    if not isinstance(valor, int):
                        validacoes.append('VALOR PRECISA SER UM NÚMERO INTEIRO, ')
                    elif valor < 0:
                        validacoes.append('VALOR NÃO PODE SER NEGATIVO, ')

                if attr in ['RUBRICA']:
                    req = obter_tipos_rubricas()
                    encontrou = False
                    for tipos in req:
                        if str(tipos["id_rubrica"]) == atributos.get('RUBRICA'):
                            encontrou = True
                    if encontrou == False:
                        validacoes.append('RUBRICA NÃO EXISTE, ')

                if attr in ['CONTA CORRENTE']:
                    req = obter_contas_bancarias()
                    encontrou = False
                    for tipos in req:
                        conta = f"{tipos["CODIGO_CC"]}-{tipos["DIGITO_CC"]}"
                        if str(conta) == str(atributos.get('CONTA CORRENTE')):
                            encontrou = True
                    if encontrou == False:
                        validacoes.append('CONTA CORRENTE NÃO EXISTE, ')

                if attr in ['TIPO DE DESPESA']:
                    req = obter_tipos_despesas()
                    encontrou = False
                    for tipos in req:
                        if str(tipos["cod_despesa"]) == atributos.get('TIPO DE DESPESA'):
                            encontrou = True
                    if encontrou == False:
                        validacoes.append('TIPO DE DESPESA NÃO EXISTE, ')

                if attr in ['TIPO DE DOCUMENTO']:
                    req = obter_tipos_documentos()
                    encontrou = False
                    for tipos in req:
                        if str(tipos["cod_tipo_documento"]) == atributos.get('TIPO DE DOCUMENTO'):
                            encontrou = True
                            if atributos.get('TIPO DE DOCUMENTO') == 'NF':
                                if not atributos.get('SERIE') or not atributos.get('NUMERO DO DOCUMENTO') or not atributos.get(
                                        'CODIGO FISCAL'):
                                    validacoes.append('NUMERO DO DOCUMENTO, SERIE E CODIGO FISCAL DEVEM SER PREENCHIDOS NO ARQUIVO SE TIPO DE DOCUMENTO FOR NF, ')
                    if encontrou == False:
                        validacoes.append('TIPO DE DOCUMENTO NÃO EXISTE, ')

                self.preencher_validacao(idx, validacoes)
        return self.df

RegistryValidators.register_alt_exc('DESPESAS', DespesasValidator)