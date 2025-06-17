from models.base_validador import BaseValidator
from models.common import LISTA_ATRIBUTOS_SALDOS
import re
import pandas as pd
from utils.utils import erros, obter_contratos
from utils.tratamentos import limpar_dados, padronizar_texto, verificar_formato_brasileiro, string_to_float
from models.registry import RegistryValidators

class SaldosValidator(BaseValidator):
    def __init__(self, df, tipo_de_acao):
        super().__init__(df, tipo_de_acao)
        self.valid_attributes = LISTA_ATRIBUTOS_SALDOS

    def validar_alteracao(self):

        for id, grupo in self.df.groupby('ID'):
            for idx, row in grupo.iterrows():
                validacoes = []
                attr = row['ATRIBUTO']
                valor = row['NOVO_VALOR']
                if attr in ['VALOR EM CONTA CORRENTE', 'APLICACAO FINANCEIRA', 'PROVISAO', 'VALOR EM ESPECIE']:
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

                    if attr != 'VALOR EM CONTA CORRENTE' and float(valor) < 0:
                        validacoes.append('VALOR NÃO PODE SER NEGATIVO')

                elif attr == 'IMAGEM DO EXTRATO':
                    if not isinstance(valor, str):
                        validacoes.append('DESCRICAO INVALIDA, ')

                    valor = str(valor).strip()

                    # Verifica se termina com .pdf (em minúsculo)
                    if not valor.lower().endswith('.pdf'):
                        validacoes.append('IMAGEM DO EXTRATO DEVE TERMINAR COM .pdf, ')
                    else:
                        # Garante que .pdf está em minúsculo
                        if not valor.endswith('.pdf'):
                            validacoes.append('A EXTENSÃO .pdf DEVE SER MINÚSCULA, ')

                    # Remove a extensão .pdf para validar o nome do arquivo
                    nome_arquivo = valor[:-4] if valor.lower().endswith('.pdf') else valor

                    # Verifica o comprimento (considerando os 4 caracteres de .pdf)
                    if len(valor) > 150:
                        validacoes.append('IMAGEM DO EXTRATO MAIOR QUE 150 CARACTERES, ')

                    # Verifica se o nome do arquivo (sem .pdf) contém apenas letras, números e underline
                    if not re.fullmatch(r'^[A-Z0-9_]+$', nome_arquivo):
                        validacoes.append('IMAGEM DO EXTRATO SÓ PODE CONTER LETRAS MAIÚSCULAS, NÚMEROS E UNDERLINE (_), ')

                self.preencher_validacao(idx, validacoes)
        return self.df

RegistryValidators.register_alt_exc('SALDOS', SaldosValidator)