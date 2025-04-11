from models.base_df import BaseDFImportacao

class ContratosTerceirosDFImportacao (BaseDFImportacao):
    def __init__(self, dataframe = None, base_url=None, listaOS=None, progress_bar = None, modulo = None, tipo_arquivo = None):
        super().__init__(dataframe, base_url, listaOS, progress_bar, modulo, tipo_arquivo)
        self.nome_classe = 'CONTRATOS DE TERCEIROS'

    def load_lists_from_osinfo_subclasse(self):
        self.load_unit_list_by_os_contract_unit_type()

    def check_df_data_subclasse(self, index):
        problemas = []
        problemas.append(self.check_mandatory_fields(index))
        problemas.append(self.check_full_dates(index))
        problemas.append(self.check_short_dates(index))
        problemas.append(self.check_pdf(self.df.at[index, 'IMG_CONTRATO']))
        problemas.append(self.check_cnpj(index))
        problemas.append(self.check_currency_values_br(index))
        problemas.append(self.check_chars_len(index))
        return problemas
