from models.base_validador import BaseValidatorIns
from models.registry import RegistryValidators
import datetime
from models.common import CONFIGURACOES_MODULOS
import pandas as pd
from utils.utils import obter_tipos_de_vinculo

class VinculosDeTrabalhoValidator(BaseValidatorIns):
    def __init__(self, df):
        super().__init__(df)
        self.modulo = 'vinculo'  # Identifica o tipo de módulo
        self.config = CONFIGURACOES_MODULOS['modulo_vinculos']
        self.cabecalho_str = self.config['cabecalho_str']
        self.cabecalho = self.trata_cabecalho(self.cabecalho_str)
        self.datas_abreviadas = self.config['datas_abreviadas']
        self.datas_completas = self.config['datas_completas']
        self.campos_obrigatorios = self.config['campos_obrigatorios']
        self.campos_monetarios = self.config['campos_monetarios']
        self.limites_tamanho = self.config['limites_tamanho']

        self.campos_cpf = ['CPF']
        self.campos_inteiros = ['COD_OS', 'CARGA_HORARIA', 'CNES', 'CATEGORIA']
        self.campo_contrato = []
        self.tipos_de_vinculo = [str(d["tpvc_cd_tipo_vinculacao"]) for d in obter_tipos_de_vinculo()]

    def validar_especifico(self):
        self.validar_inteiros()
        self.validar_datas()
        self.validar_tamanho_campos()
        self.validar_cpf()
        self.validar_tipo_de_vinculo()
        self.validar_campo_ativo()
        self.validar_datas_admissao_demissao()
        self.validar_campos_conselho()
        self.validar_campo_cnes()
        
    def validar_campo_ativo(self):
        """Valida se o campo ATIVO contém apenas 'S' ou 'N'"""
        if 'ATIVO' in self.df.columns:
            for idx, valor in self.df['ATIVO'].items():
                if pd.notna(valor):
                    valor_str = str(valor).strip().upper()
                    if valor_str not in ['S', 'N']:
                        self._registrar_erro(idx, "ATIVO: Deve ser 'S' (Sim) ou 'N' (Não).")
                        
    def validar_datas_admissao_demissao(self):
        """Valida as datas de admissão e demissão"""
        from datetime import datetime
        

        for idx, row in self.df.iterrows():
            data_admissao = row.get('DATA_ADMISSAO')
            data_demissao = row.get('DATA_DEMISSAO')
            ativo = row.get('ATIVO')
            
            if pd.notna(data_admissao):
                try:
                    data_adm = pd.to_datetime(data_admissao).date()
                        
                except (ValueError, TypeError):
                    self._registrar_erro(idx, "DATA_ADMISSAO: Formato de data inválido.")
                    continue
            else:
                self._registrar_erro(idx, "DATA_ADMISSAO: Campo obrigatório não preenchido.")
                continue
                
            if pd.notna(ativo):
                ativo_str = str(ativo).strip().upper()
                
                if ativo_str == 'S':
                    if pd.notna(data_demissao):
                        self._registrar_erro(idx, "DATA_DEMISSAO: Não pode estar preenchida quando ATIVO = 'S' (funcionário ativo).")
                elif ativo_str == 'N':
                    if pd.isna(data_demissao):
                        self._registrar_erro(idx, "DATA_DEMISSAO: Deve estar preenchida quando ATIVO = 'N' (funcionário inativo).")
                    else:
                        try:
                            data_dem = pd.to_datetime(data_demissao).date()
                            if data_dem <= data_adm:
                                self._registrar_erro(idx, "DATA_DEMISSAO: Deve ser posterior à DATA_ADMISSAO.")
                                
                        except (ValueError, TypeError):
                            self._registrar_erro(idx, "DATA_DEMISSAO: Formato de data inválido.")
                 
    def validar_campos_conselho(self):
        """Valida os campos relacionados ao conselho profissional"""
        import re
        
        for idx, row in self.df.iterrows():
            conselho = row.get('CONSELHO')
            num_reg_profissional = row.get('NUM_REG_PROFISSIONAL')
            uf_conselho = row.get('UF_CONSELHO')
            cbo = row.get('CBO')
            
                    
            if pd.notna(conselho) and pd.isna(num_reg_profissional):
                self._registrar_erro(idx, "NUM_REG_PROFISSIONAL: Campo obrigatório quando CONSELHO está preenchido.")
                    
            if pd.notna(conselho) and pd.notna(num_reg_profissional) and pd.isna(uf_conselho):
                self._registrar_erro(idx, "UF_CONSELHO: Campo obrigatório quando CONSELHO e NUM_REG_PROFISSIONAL estão preenchidos.")
                    
            if pd.notna(conselho) or pd.notna(num_reg_profissional) or pd.notna(uf_conselho):
                if pd.isna(cbo):
                    self._registrar_erro(idx, "CBO: Campo obrigatório quando qualquer campo de conselho está preenchido.")
                else:
                    cbo_str = str(cbo).strip()
                    if not re.match(r'^\d{4}-\d{2}$', cbo_str):
                        self._registrar_erro(idx, "CBO: Formato inválido. Use o formato NNNN-NN (ex: 2251-12).")
                        
    def validar_campo_cnes(self):
        """Valida se o campo CNES é obrigatório para determinados COD_OS"""
        codigos_os_cnes_obrigatorio = [
            268, 10358, 9739, 11659, 265, 259, 9615, 10893, 
            261, 10040, 9900, 9612, 263, 264, 11225
        ]
        
        for idx, row in self.df.iterrows():
            cod_os = row.get('COD_OS')
            cnes = row.get('CNES')
            
            if pd.notna(cod_os) and int(cod_os) in codigos_os_cnes_obrigatorio:
                if pd.isna(cnes):
                    self._registrar_erro(idx, f"CNES: Campo obrigatório para SMS.")

RegistryValidators.register_ins('modulo_vinculos', VinculosDeTrabalhoValidator)
