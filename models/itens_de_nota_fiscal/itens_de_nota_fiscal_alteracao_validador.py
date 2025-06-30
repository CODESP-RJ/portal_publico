from models.base_validador import BaseValidator
from models.common import LISTA_ATRIBUTOS_ITENS_DE_NOTA_FISCAL
import re
import pandas as pd
from utils.utils import erros, obter_contratos
from utils.tratamentos import limpar_dados, padronizar_texto, verificar_formato_brasileiro, string_to_float, formata_cnpj
from models.registry import RegistryValidators

class ItensDeNotaFiscalValidator(BaseValidator):
    def __init__(self, df, tipo_de_acao):
        super().__init__(df, tipo_de_acao)
        self.valid_attributes = LISTA_ATRIBUTOS_ITENS_DE_NOTA_FISCAL

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

                if attr in ['CODIGO DO SERVICO', 'CODIGO DO MATERIAL']:
                    if atributos.get('CODIGO DO SERVICO') and atributos.get('CODIGO DO MATERIAL'):
                        validacoes.append('DADOS DE SERVIÇO E MATERIAL (UM DELES PRECISA ESTAR VAZIO PARA REALIZARMOS A TROCA), ')
                if attr in ['CODIGO DO SERVICO', 'CODIGO DO MATERIAL',
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
                        # Verifica formato específico para cada tipo de valor
                        if attr == 'VALOR UNITARIO':
                            if not verificar_formato_brasileiro(valor, casas_decimais=4):
                                validacoes.append(
                                    'FORMATO INVÁLIDO PARA VALOR UNITÁRIO (USE . PARA MILHARES E , DECIMAL COM 4 CASAS)')
                                continue
                        else:  # VALOR TOTAL
                            if not verificar_formato_brasileiro(valor, casas_decimais=2):
                                validacoes.append(
                                    'FORMATO INVÁLIDO PARA VALOR TOTAL (USE . PARA MILHARES E , DECIMAL COM 2 CASAS)')
                                continue

                        try:
                            valor = float(string_to_float(str(valor)))
                        except ValueError:
                            validacoes.append('VALOR INVÁLIDO (NÃO NUMÉRICO)')
                            self.df.at[idx, 'VALIDACAO'] = '\n'.join(validacoes) if validacoes else 'OK'
                            continue

                    if float(valor) < 0:
                        validacoes.append('VALOR NÃO PODE SER NEGATIVO')

                self.preencher_validacao(idx, validacoes)
        return self.df

RegistryValidators.register_alt_exc('ITENS DE NOTA FISCAL', ItensDeNotaFiscalValidator)