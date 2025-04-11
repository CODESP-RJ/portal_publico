import requests
import re
import pandas as pd
import streamlit as st
from models.base_df import BaseDFImportacao
import json

class DespesasDFImportacao (BaseDFImportacao):
    def __init__(self, dataframe = None, base_url=None, listaOS=None, progress_bar = None, modulo = None, tipo_arquivo = None):
        super().__init__(dataframe, base_url, listaOS, progress_bar, modulo, tipo_arquivo)
        self.nome_classe = 'DESPESAS'

    def load_lists_from_osinfo_subclasse(self):
        # self.load_bank_account_by_contract_id()
        # self.load_unit_list_by_os_contract_unit_type()
        self.load_document_type_list()
        self.load_expense_type_list()
        self.load_expenditures_list()

    def check_df_data_subclasse(self, index):
        problemas = []
        problemas.append(self.check_mandatory_fields(index))
        problemas.append(self.check_integrity_fisica_vs_juridica(index))
        problemas.append(self.check_tipo_despesa(index))
        problemas.append(self.check_rubrica(index))
        problemas.append(self.check_tipo_documento(index))
        problemas.append(self.check_integrity_TipoNF_vs_NumDocumento(index))
        problemas.append(self.check_conta_bancaria(index))
        problemas.append(self.check_full_dates(index))
        problemas.append(self.check_short_dates(index))
        problemas.append(self.check_pdf(self.df.at[index, 'DESCRICAO']))
        problemas.append(self.check_cpf(index))
        problemas.append(self.check_cnpj(index))
        problemas.append(self.check_currency_values_br(index))
        problemas.append(self.check_chars_len(index))
        return problemas