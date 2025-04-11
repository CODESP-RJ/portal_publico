import requests
import pandas as pd
import streamlit as st
from models.base_df import BaseDFImportacao


class BensPatrimoniadosDFImportacao (BaseDFImportacao):
    def __init__(self, dataframe = None, base_url=None, listaOS=None, progress_bar = None, modulo = None, tipo_arquivo = None):
        super().__init__(dataframe, base_url, listaOS, progress_bar, modulo, tipo_arquivo)
        self.nome_classe = 'BENS PATRIMONIADOS'

    def load_lists_from_osinfo_subclasse(self):
        self.load_unit_list_by_os_contract_unit_type()
        self.load_asset_types()

    def check_df_data_subclasse(self, index):
        problemas = []
        problemas.append(self.check_mandatory_fields(index))
        problemas.append(self.check_asset_type(index))
        problemas.append(self.check_full_dates(index))
        problemas.append(self.check_short_dates(index))
        problemas.append(self.check_pdf(self.df.at[index, 'IMG_NF']))
        problemas.append(self.check_cnpj(index))
        problemas.append(self.check_currency_values_br(index))
        problemas.append(self.check_chars_len(index))
        return problemas

    def check_asset_type(self, index):
        resultado = ''
        valor = self.df.at[index, 'COD_TIPO']
        dfFiltrado = self.dfTiposBens.loc[ self.dfTiposBens['id_bem_tipo'].astype(int) == int(valor) ]
        if dfFiltrado.empty:
            resultado = f"O COD_TIPO de BEM não é valido ({valor})"
        return resultado    
    
    def load_asset_types(self):
        self.dfTiposBens = pd.DataFrame()
        url = self.base_url + '/asset/server/assetService/getAssetTypes'
        try:
            requisicao = requests.post(url, cookies={"osinfo":f"{st.secrets['cookie']}"})
            requisicao.raise_for_status()
            self.dfTiposBens = pd.DataFrame(data=requisicao.json())
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro ao obter lista de tipos de bens: {e}")            