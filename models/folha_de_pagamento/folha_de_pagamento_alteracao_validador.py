from models.base_validador import BaseValidator
from models.common import LISTA_ATRIBUTOS_FOLHA_DE_PAGAMENTO
import re
import pandas as pd
from utils.utils import erros, obter_tipos_de_vinculo
from utils.tratamentos import limpar_dados, padronizar_texto, string_to_float, formata_cpf, formata_cnpj, verificar_formato_brasileiro, validar_data_brasileira
from models.registry import RegistryValidators
from datetime import datetime

class FolhaDePagamentoValidador(BaseValidator):
    def __init__(self, df, tipo_de_acao):
        super().__init__(df, tipo_de_acao)
        self.valid_attributes = LISTA_ATRIBUTOS_FOLHA_DE_PAGAMENTO

    def validar_alteracao(self):

        for id, grupo in self.df.groupby('ID'):
            atributos = grupo.set_index('ATRIBUTO')['NOVO_VALOR'].to_dict()
            atributos = {k: (None if pd.isna(v) else v) for k, v in atributos.items()}
            datas_licenca = {}
            for idx, row in grupo.iterrows():
                validacoes = []
                attr = row['ATRIBUTO']
                valor = row['NOVO_VALOR']

                if not valor or pd.isna(valor) or str(valor).strip() == '':
                    self.df.at[idx, 'VALIDACAO'] = 'INVALIDO VALOR VAZIO OU NULO, '
                    continue

                if attr in ['UNIDADE', 'CARGA HORARIA EFETIVA', 'PERCENTUAL DE RATEIO']:
                    try:
                        valor_int = int(valor)
                        if valor_int < 0:
                            validacoes.append('VALOR NÃO PODE SER NEGATIVO, ')
                    except ValueError:
                        validacoes.append('VALOR PRECISA SER UM NÚMERO INTEIRO, ')

                if attr in ['DATA LICENCA INICIO', 'DATA LICENCA FIM']:
                    if not validar_data_brasileira(valor):
                        validacoes.append(f'{attr} DEVE ESTAR NO FORMATO DD/MM/YYYY, ')
                    else:
                        try:
                            datas_licenca[attr] = datetime.strptime(valor, '%d/%m/%Y')
                        except ValueError:
                            validacoes.append(f'{attr} COM FORMATO INVÁLIDO, ')

                if 'DATA LICENCA INICIO' in datas_licenca and 'DATA LICENCA FIM' in datas_licenca:
                    if datas_licenca['DATA LICENCA FIM'] < datas_licenca['DATA LICENCA INICIO']:
                        validacoes.append('DATA LICENCA FIM NÃO PODE SER ANTERIOR À DATA LICENCA INICIO, ')

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
                    except ValueError:
                        validacoes.append(f'{attr.upper()} NÃO É UM NÚMERO VÁLIDO, ')

                if attr in LISTA_ATRIBUTOS_FOLHA_DE_PAGAMENTO and attr not in ["VINCULO", "UNIDADE", "MES DE COMPETENCIA", "ANO DE COMPETENCIA", "CARGA HORARIA EFETIVA", "PERCENTUAL DE RATEIO", "DATA LICENCA INICIO", "DATA LICENCA FIM", "OBSERVACAO"]:
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

RegistryValidators.register_alt_exc('FOLHA DE PAGAMENTO', FolhaDePagamentoValidador)