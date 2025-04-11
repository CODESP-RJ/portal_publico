import pandas as pd
import base64

class Dataframeutils:
    @staticmethod 
    def adiciona_linhas_erro(df_principal, df_erro, mensagem_erro, coluna_erro='ERROS'):
        if df_principal is None:
            df_principal = pd.DataFrame()
            
        if coluna_erro not in df_principal.columns:
            df_principal[coluna_erro] = ''

        # Criar uma cópia do df_erro para evitar o SettingWithCopyWarning
        df_erro_copy = df_erro.copy()
        df_erro_copy[coluna_erro] = mensagem_erro
        
        # Concatenar usando concat
        df_principal = pd.concat([df_principal, df_erro_copy], ignore_index=True)
        
        return df_principal

    @staticmethod
    def convert_df_to_csv(df):
        csv = df.to_csv(index=False, sep=';')
        return csv

    @staticmethod
    def get_download_link(df):
        csv = Dataframeutils.convert_df_to_csv(df)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="AlteraçoesNaoAtendidasDespesa.csv">Clique aqui para baixar o CSV com somente as linhas que não foram atendidas</a>'
        return href