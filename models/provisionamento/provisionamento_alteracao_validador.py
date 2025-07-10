from models.base_validador import BaseValidator
from models.common import LISTA_ATRIBUTOS_FOLHA_DE_PAGAMENTO, LISTA_ATRIBUTOS_PROVISIONAMENTO
import re
import pandas as pd
from utils.utils import erros, obter_tipos_de_vinculo
from utils.tratamentos import limpar_dados, padronizar_texto, string_to_float, formata_cpf, formata_cnpj, verificar_formato_brasileiro, validar_data_brasileira
from models.registry import RegistryValidators
from datetime import datetime

class ProvisionamentoValidador(BaseValidator):
    def __init__(self, df, tipo_de_acao):
        super().__init__(df, tipo_de_acao)
        self.valid_attributes = LISTA_ATRIBUTOS_PROVISIONAMENTO

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

                datas_licenca = {}

                if attr in ['UNIDADE']:
                    try:
                        valor_int = int(valor)
                        if valor_int < 0:
                            validacoes.append('VALOR NÃO PODE SER NEGATIVO, ')
                    except ValueError:
                        validacoes.append('VALOR PRECISA SER UM NÚMERO INTEIRO, ')

                if attr in ['VINCULO']:
                    req = obter_tipos_de_vinculo()
                    encontrou = False
                    for tipos in req:
                        if str(tipos["tpvc_cd_tipo_vinculacao"]) == atributos.get('VINCULO'):
                            encontrou = True
                    if encontrou == False:
                        validacoes.append('TIPO DE VINCULO NÃO EXISTE, ')

                if attr in ['MES DE COMPETENCIA', 'ANO DE COMPETENCIA']:
                    try:
                        valor_int = int(valor)
                        if valor_int < 0:
                            validacoes.append(f'{attr.upper()} NÃO PODE SER NEGATIVO, ')
                        if attr == "MES DE COMPETENCIA" and (valor_int > 12 or valor_int < 1):
                            validacoes.append(f'{attr.upper()} DEVE SER ENTRE 1 E 12, ')
                        if attr == "ANO DE COMPETENCIA" and (valor_int < 2000):
                            validacoes.append(f'{attr.upper()} DEVE SER MAIOR QUE 2000, ')
                    except ValueError:
                        validacoes.append(f'{atributo.upper()} NÃO É UM NÚMERO VÁLIDO, ')

                if attr in LISTA_ATRIBUTOS_PROVISIONAMENTO and attr not in ["VINCULO", "UNIDADE", "MES DE COMPETENCIA", "ANO DE COMPETENCIA"]:
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

                self.preencher_validacao(idx, validacoes)
        return self.df

RegistryValidators.register_alt_exc('PROVISIONAMENTO', ProvisionamentoValidador)