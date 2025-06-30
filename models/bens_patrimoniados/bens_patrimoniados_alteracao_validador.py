from models.base_validador import BaseValidator
from models.common import LISTA_ATRIBUTOS_BENS_PATRIMONIADOS
import re
import pandas as pd
from utils.tratamentos import string_to_float, formata_cpf, formata_cnpj
from utils.utils import erros, obter_contratos, obter_tipos_bens
from utils.tratamentos import limpar_dados, padronizar_texto, verificar_formato_brasileiro, string_to_float
from models.registry import RegistryValidators

class BensPatrimoniadosValidator(BaseValidator):
    def __init__(self, df, tipo_de_acao):
        super().__init__(df, tipo_de_acao)
        self.valid_attributes = LISTA_ATRIBUTOS_BENS_PATRIMONIADOS

    def validar_alteracao(self):

        for id, grupo in self.df.groupby('ID'):
            atributos = grupo.set_index('ATRIBUTO')['NOVO_VALOR'].to_dict()
            atributos = {k: (None if pd.isna(v) else v) for k, v in atributos.items()}
            for idx, row in grupo.iterrows():
                validacoes = []
                attr = row['ATRIBUTO']
                valor = row['NOVO_VALOR']

                if not valor or pd.isna(valor) or str(valor).strip() == '':
                    self.df.at[idx, 'VALIDACAO'] = 'INVALIDO VALOR VAZIO OU NULO, '
                    continue

                if attr in ['VALOR']:
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

                    if float(valor) < 0:
                        validacoes.append('VALOR NÃO PODE SER NEGATIVO')

                if attr in ['NOME ARQUIVO IMAGEM']:
                    if not isinstance(valor, str):
                        validacoes.append('NOME ARQUIVO IMAGEM INVALIDA, ')

                    valor = str(valor).strip()

                    # Verifica se termina com .pdf (em minúsculo)
                    if not valor.lower().endswith('.pdf'):
                        validacoes.append('NOME ARQUIVO IMAGEM DEVE TERMINAR COM .pdf, ')
                    else:
                        # Garante que .pdf está em minúsculo
                        if not valor.endswith('.pdf'):
                            validacoes.append('A EXTENSÃO .pdf DEVE SER MINÚSCULA, ')

                    # Remove a extensão .pdf para validar o nome do arquivo
                    nome_arquivo = valor[:-4] if valor.lower().endswith('.pdf') else valor

                    # Verifica o comprimento (considerando os 4 caracteres de .pdf)
                    if len(valor) > 150:
                        validacoes.append('NOME ARQUIVO IMAGEM MAIOR QUE 150 CARACTERES, ')

                    # Verifica se o nome do arquivo (sem .pdf) contém apenas letras, números e underline
                    if not re.fullmatch(r'^[A-Z0-9_]+$', nome_arquivo):
                        validacoes.append('NOME ARQUIVO IMAGEM SÓ PODE CONTER LETRAS MAIÚSCULAS, NÚMEROS E UNDERLINE (_), ')

                if attr in ['VIDA UTIL', 'CONTROLE', 'NOTA FISCAL', 'QUANTIDADE', 'TIPO', 'UNIDADE']:
                    if isinstance(valor, str):
                        try:
                            valor = int(valor)
                        except ValueError:
                            validacoes.append('VALOR INVÁLIDO (NÃO NUMÉRICO), ')
                            valor = None
                    if isinstance(valor, int) and valor < 0:
                        validacoes.append('VALOR NÃO PODE SER NEGATIVO, ')

                if attr in ['CNPJ', 'RAZAO SOCIAL']:
                    if not (atributos.get('CNPJ') and atributos.get('RAZAO SOCIAL')):
                            validacoes.append('DADOS INCOMPLETOS PARA PESSOA JURÍDICA, ')

                if attr in ['CNPJ']:
                    if (atributos.get('CNPJ')):
                        valor_split = atributos.get('CNPJ').split(' ')[0]
                        if formata_cnpj(valor_split) == 'invalido':
                            validacoes.append('CNPJ INVALIDO, ')

                if attr in ['RAZAO SOCIAL']:
                    if (atributos.get('RAZAO SOCIAL')):
                        if not isinstance(atributos.get('RAZAO SOCIAL'), str):
                            validacoes.append('RAZAO SOCIAL INVALIDO, ')
                        valor = atributos.get('RAZAO SOCIAL').strip()
                        if len(valor) > 100:
                            validacoes.append('RAZAO SOCIAL MAIOR QUE 100 CARACTERES, ')
                        if not re.fullmatch(r'[a-zA-Z0-9\sà-üÀ-ÜçÇéÉãÃõÕôÔîÎûÛ\.,\-_&/\()\?%]+', valor):
                            validacoes.append('RAZAO SOCIAL CONTEM CARACTERES INVALIDOS, ')

                    if not (atributos.get('CNPJ') and atributos.get('RAZAO SOCIAL')):
                        validacoes.append('DADOS INCOMPLETOS PARA PESSOA JURÍDICA, ')

                if attr in ['CONTROLE']:
                    if isinstance(valor, str) and len(valor) > 50:
                        validacoes.append('CONTROLE MAIOR QUE 50 CARACTERES, ')

                if attr in ['DESCRICAO']:
                    if isinstance(valor, str) and len(valor) > 255:
                        validacoes.append('CONTROLE MAIOR QUE 255 CARACTERES, ')

                if attr in ['VINCULACAO']:
                    if isinstance(valor, str) and len(valor) > 255:
                        validacoes.append('CONTROLE MAIOR QUE 255 CARACTERES, ')

                if attr in ['NOTA FISCAL']:
                    if isinstance(valor, str) and len(valor) > 20:
                        validacoes.append('NOTA FISCAL MAIOR QUE 20 CARACTERES, ')

                if attr in ['TIPO']:
                    req = obter_tipos_bens()
                    encontrou = False
                    for tipos in req:
                        if int(tipos["id_bem_tipo"]) == int(atributos.get('TIPO')):
                            encontrou = True
                    if encontrou == False:
                        validacoes.append('TIPO DE BEM NÃO EXISTE, ')

                self.preencher_validacao(idx, validacoes)
        return self.df

RegistryValidators.register_alt_exc('BENS PATRIMONIADOS', BensPatrimoniadosValidator)