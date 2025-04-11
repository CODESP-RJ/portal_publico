from models.base_df import BaseDFImportacao

class FornecedoresDFImportacao (BaseDFImportacao):
    def __init__(self, dataframe = None, base_url=None, listaOS=None, progress_bar = None, modulo = None, tipo_arquivo = None):
        super().__init__(dataframe, base_url, listaOS, progress_bar, modulo, tipo_arquivo)
        self.nome_classe = 'FORNECEDORES'

    def check_df_data_subclasse(self, index):
        problemas = []
        problemas.append(self.check_mandatory_fields(index))
        problemas.append(self.check_cnpj_cpf(index))
        problemas.append(self.check_email(index))
        problemas.append(self.check_tipo_fornecedor(index))
        return problemas

    def check_tipo_fornecedor(self, index):
        cnpj_cpf = self.df.at[index, 'CNPJ_CPF']
        tipo = self.df.at[index, 'TIPO']
        expected = 'J' if isinstance(cnpj_cpf, str) and '/' in cnpj_cpf else 'F'
        if tipo != expected:
            return f"Coluna TIPO inválida ({tipo}); esperado '{expected}' para CNPJ_CPF {cnpj_cpf}"
        return ''