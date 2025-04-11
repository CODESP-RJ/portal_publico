import requests
import pandas as pd
import streamlit as st
from models.base_df import BaseDFImportacao

class ItensNotaFiscalDFImportacao (BaseDFImportacao):
    def __init__(self, dataframe = None, base_url=None, listaOS=None, progress_bar = None, modulo = None, tipo_arquivo = None):
        super().__init__(dataframe, base_url, listaOS, progress_bar, modulo, tipo_arquivo)
        self.nome_classe = 'ITENS NOTA FISCAL'
        self.checked_sigma_number = pd.DataFrame()

    def load_lists_from_osinfo_subclasse(self):
        pass

    def load_lists_from_osinfo(self, index, nome_coluna = 'COD_CONTRATO'):
        pass

    def check_df_data_subclasse(self, index):
        problemas = []
        problemas.append(self.check_mandatory_fields(index))
        problemas.append(self.check_tipo_item(index))
        problemas.append(self.check_short_dates(index))
        problemas.append(self.check_cnpj(index, 'CNPJ_FORN'))
        problemas.append(self.check_currency_values_br(index))
        problemas.append(self.check_chars_len(index))
        problemas.append(self.check_sigma_number(index))
        return problemas

    def check_tipo_item(self, index):
        resultado = ''
        valor = str(self.df.at[index, 'MAT_OU_SERV'])
        if not valor in ['S', 'M']:
            resultado = f"O TIPO de documento não é valido ({valor})"
        return resultado
    
    def check_sigma_number(self, index):
        url = self.base_url + '/sigma/server/sigmaService/getItemsServiceListAutoComplete'
        try:
            sigma = 'd=' + str(self.df.at[index, 'COD_MAT_SERV'])
            requisicao = requests.post(url, data=sigma, cookies={"osinfo":f"{st.secrets['cookie']}"})
            requisicao.raise_for_status()
            dados_sigma = pd.DataFrame(data=requisicao.json())
            if dados_sigma.empty:
                return f"O código Sigma na coluna COD_MAT_SERV nao foi encontrado."
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro ao obter lista de tipos de documentos: {e}")    