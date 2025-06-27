from models.base_validador import BaseValidatorIns
from models.registry import RegistryValidators
import datetime
from models.common import CONFIGURACOES_MODULOS
import pandas as pd

class ItensNotaFiscalValidator(BaseValidatorIns):
    def __init__(self, df):
        super().__init__(df)
        self.config = CONFIGURACOES_MODULOS['modulo_itens_nota_fiscal']
        self.cabecalho_str = self.config['cabecalho_str']
        self.cabecalho = self.trata_cabecalho(self.cabecalho_str)
        self.datas_abreviadas = self.config['datas_abreviadas']
        self.datas_completas = self.config['datas_completas']
        self.campos_obrigatorios = self.config['campos_obrigatorios']
        self.campos_monetarios = self.config['campos_monetarios']
        self.limites_tamanho = self.config['limites_tamanho']
        self.campo_contrato = []

        self.campos_cnpj = ['CNPJ_FORN']
        self.campos_inteiros = ['NUM_OS', 'COD_MAT_SERV']

    def _validar_unidades_de_medida(self, base_sigma, coluna_unidade, codigo, idx, coluna_codigo_sigma):
        """Valida a unidade de medida contra a base Sigma"""
        if codigo and not base_sigma.empty:
            # Busca o código correspondente na base Sigma
            registro_sigma = base_sigma[base_sigma[coluna_codigo_sigma].str.strip() == codigo.strip()]

            if not registro_sigma.empty:
                # Pega a unidade de medida da base Sigma
                unidade_sigma = registro_sigma.iloc[0][coluna_unidade]
                unidade_sigma = str(unidade_sigma).strip() if pd.notna(unidade_sigma) else None

                # Pega a unidade informada pelo usuário
                unidade_informada = str(self.df.at[idx, 'UNID_MED']).strip() if pd.notna(
                    self.df.at[idx, 'UNID_MED']) else None

                # Comparação case-sensitive
                if unidade_informada != unidade_sigma:
                    self._registrar_erro(
                        idx,
                        f"UNID_MED: Unidade de medida inválida para o código {codigo}. "
                        f"Esperado: {unidade_sigma}"
                    )

    def validar_campos_cod(self):
        if 'MAT_OU_SERV' in self.df.columns and 'COD_MAT_SERV' in self.df.columns:
            for idx, row in self.df.iterrows():
                valor = row['MAT_OU_SERV']
                codigo = str(row['COD_MAT_SERV']).strip() if pd.notna(row['COD_MAT_SERV']) else None

                if pd.notna(valor):
                    valor = str(valor).strip().upper()
                    if valor == 'M':
                        try:
                            materiais_df = pd.read_excel(
                                'download/tabelas_auxiliares/MATERIAIS.xls',
                                dtype={'sigm_cd_item': str}
                            )
                            if codigo and not materiais_df['sigm_cd_item'].str.strip().isin([codigo]).any():
                                self._registrar_erro(
                                    idx,
                                    f"COD_MAT_SERV: Código {codigo} não encontrado na base sigma de materiais."
                                )

                            self._validar_unidades_de_medida(
                                base_sigma=materiais_df,
                                coluna_unidade='sigm_unidade_medida',
                                coluna_codigo_sigma='sigm_cd_item',
                                codigo=codigo,
                                idx=idx
                            )
                        except FileNotFoundError:
                            print("Arquivo de materiais auxiliares não encontrado.")
                            return
                elif valor == 'S':
                    try:
                        servicos_df = pd.read_excel(
                            'download/tabelas_auxiliares/SERVICOS.xls',
                            dtype={'Código do Serviço': str}
                        )
                    except FileNotFoundError:
                        print("Arquivo de serviços auxiliares não encontrado.")
                        return
                    except Exception as e:
                        print(f"Erro ao ler arquivo de serviços: {str(e)}")
                        return
                    if codigo and not servicos_df['Código do Serviço'].str.strip().str.upper().isin([codigo]).any():
                        self._registrar_erro(
                            idx,
                            f"COD_MAT_SERV: Código {codigo} não encontrado na base sigma de serviços."
                        )
                    self._validar_unidades_de_medida(servicos_df, 'UNIDADE DE MEDIDA', codigo)
                else:
                    self._registrar_erro(idx, "MAT_OU_SERV: Campo inválido. Deve ser 'M' ou 'S'.")

    def validar_especifico(self):
        self.validar_inteiros()
        self.validar_datas()
        self.validar_tamanho_campos()
        self.validar_valores_monetarios()
        self.validar_documentos_pdf()
        self.validar_cnpj()
        self.validar_campos_cod()

RegistryValidators.register_ins('modulo_itens_nota_fiscal', ItensNotaFiscalValidator)