import requests
import re
import logging
import pandas as pd
from pycpfcnpj import cpfcnpj
from models.modelos_arquivos import Cabecalho
import datetime
import streamlit as st
import json

class BaseDFImportacao:
    def __init__(self, dataframe = None, base_url=None, listaOS=None, progress_bar = None, modulo = None, tipo_arquivo = None):
        self.df = pd.DataFrame()
        if len(dataframe):
            self.df = dataframe
        
        self.df.columns = self.df.columns.str.upper()
        self.modelo = Cabecalho(modulo, tipo_arquivo)
        self.base_url = base_url
        self.instituicao = self.df[listaOS].iloc[0,0]  # Código da instituição
        self.url_pdf_formatada = ""
        self.arquivos = {}
        self.id_contrato = None
        self.pBar = progress_bar
        self.dfCodigosDespesas = pd.DataFrame()
        self.dfRubricas = pd.DataFrame()
        self.dfTiposDocumentos = pd.DataFrame()
        self.dfUnidades = pd.DataFrame()
        self.dfContasBancarias = pd.DataFrame()
        self.session = requests.Session()
        self.nome_classe = 'DEFINIR CLASSE'

    def check_header(self) -> bool:
        cabecalho = self.modelo.retorna_cabecalho()
        for col in cabecalho:
            if not col in self.df.columns:
                raise Exception(f"Coluna ({col}) não foi encontrada no cabeçalho do arquivo de importação de self.nome_classe")
        return True

    def load_lists_from_osinfo_subclasse(self):
        #sobrescrever nas classes filhas
        pass

    def load_lists_from_osinfo(self, index, nome_coluna='COD_CONTRATO'):
        result = False
        try:
            if not self.df.at[index, nome_coluna]:
                raise Exception(f"O preenchimento da coluna ({nome_coluna}) é obrigatório")

            if self.dfContratos.empty:
                raise Exception("O DataFrame dfContratos está vazio")

            if 'num_contrato' not in self.dfContratos.columns:
                raise Exception("A coluna 'num_contrato' não foi encontrada no DataFrame dfContratos")

            contract_row = self.dfContratos.loc[self.dfContratos['num_contrato'] == self.df.at[index, nome_coluna]]
            if contract_row.empty:
                raise Exception(f"Contrato {self.df.at[index, nome_coluna]} não encontrado")

            current_contract_id = contract_row['id_contrato'].values[0]
            if self.df.at[index, nome_coluna] == '' or self.id_contrato != current_contract_id:
                self.id_contrato = current_contract_id

                if self.id_contrato is None:
                    raise Exception(f"Contrato {self.df.at[0, nome_coluna]} não encontrado")

                self.load_lists_from_osinfo_subclasse()

        except Exception as e:
            msg = f"check_df_data carregamento das listagens: {e}"
            logging.error(msg)
            raise Exception(msg)
    
    def check_df_data_subclasse(self, index):
        #sobrescrever nas classes filhas
        return []

    def check_df_data(self, tipoarquivoEscolhido = None):
        qtdLinhas = self.df.shape[0]
        try:
            for index, line in self.df.iterrows():
                if self.pBar:
                    self.pBar.progress(int(((index +1 ) / qtdLinhas)*100))
                if tipoarquivoEscolhido != "Fornecedores":      
                    self.load_lists_from_osinfo(index = index)

                problemas = self.check_df_data_subclasse(index)
                problemas_validos = [p for p in problemas if p is not None]
                problemas_validos = re.sub( '^[^a-zA-Z]*', '', ( ', '.join(problemas_validos) ) )
                problemas_validos = re.sub( '( ,)+ ?', '', problemas_validos )
                self.df.at[index, 'PROBLEMAS'] = problemas_validos

            return (len(problemas) == 0)
        except Exception as e:
            msg = f"check_df_data verificação das linhas: {e}"
            logging.error(msg)
            raise Exception(msg)

    def check_mandatory_fields(self, index):
        problemas = []
        for col in self.modelo.camposObrigatorios:
            if not col in self.df.columns:
                raise Exception(f"Coluna ({col}) não foi encontrada na no cabeçalho do arquivo de importação de despesas")
            if pd.isnull(self.df.at[index, col]): 
                problemas.append('Valor ausente em ' + col )
        return ', '.join(problemas) if problemas else None

    def check_unidade(self, index):
        resultado = ''
        valor = str(self.df.at[index, 'COD_UNIDADE'])
        dfFiltrado = self.dfUnidades[ self.dfUnidades['cod_unidade'] == valor ]
        if dfFiltrado.empty:
            resultado = f"Código da UNIDADE não é valido ({valor})"
        return resultado


    def check_integrity_fisica_vs_juridica(self, index):
        # verifica se a despesa está completa de acordo com o tipo de pessoa
        # Verifica se a despesa está preenchida apenas com os campos relativos a CPF ou CNPJ
        isFisica = False
        isJuridica = False

        if not pd.isnull(self.df.at[index, 'CPF']) or not pd.isnull(self.df.at[index, 'NOME']):
            isFisica = True

        if not pd.isnull(self.df.at[index, 'CNPJ']) or not pd.isnull(self.df.at[index, 'RAZAO']):
            isJuridica = True

        if isFisica and isJuridica:
            return 'A despesa é de ambos tipos de pessoa fisica e juridica.'

        if not isFisica and not isJuridica:
            return 'A despesa não possui dados de Pessoa Física ou Juridica.'
            
        if isFisica:
            if not (self.df.at[index, 'CPF'] and self.df.at[index, 'NOME']):
                return 'Dados incompletos para pessoa fisica.'

        if isJuridica:
            if not (self.df.at[index, 'CNPJ'] and self.df.at[index, 'RAZAO']):
                return 'Dados incompletos para pessoa juridica.'

    def check_tipo_despesa(self, index):
        resultado = ''
        valor = str(self.df.at[index, 'DESPESA'])
        dfFiltrado = self.dfCodigosDespesas[ self.dfCodigosDespesas['cod_despesa'] == valor ]
        if dfFiltrado.empty:
            resultado = f"Código de DESPESA não é valido ({valor})"
        return resultado

    def check_rubrica(self, index):
        resultado = ''
        valor = self.df.at[index, 'RUBRICA']
        dfFiltrado = self.dfRubricas[ self.dfRubricas['id_rubrica'] == int(valor) ]
        if dfFiltrado.empty:
            resultado = f"A RUBRICA não é valida ({valor})"
        return resultado

    def check_tipo_documento(self, index):
        resultado = ''
        valor = str(self.df.at[index, 'TIPO']).strip()
        dfFiltrado = self.dfTiposDocumentos[
            self.dfTiposDocumentos['cod_tipo_documento'].astype(str).str.strip().str.upper() == valor.upper()
            ]
        if dfFiltrado.empty:
            resultado = f"O TIPO de documento não é válido ({valor})"
        return resultado
    def check_integrity_TipoNF_vs_NumDocumento(self, index):
        if not pd.isnull(self.df.at[index, 'TIPO']) and self.df.at[index, 'TIPO'] == 'NF':
            if pd.isnull(self.df.at[index, 'NUM_DOCUMENTO']):
                return 'Necessário informar o Número do Documento para o Tipo de Documento de Nota Fiscal'
            if not re.fullmatch(r'[0-9]+', self.df.at[index, 'NUM_DOCUMENTO']):
                return 'Número do Documento inválido para o Tipo de Documento de Nota Fiscal'
        return ''

    def check_conta_bancaria(self, index):
        resultado = ''
    #     agencia = self.df.at[index, 'AGENCIA']
    #     conta = self.df.at[index, 'CONTA_CORRENTE']
    #     dfFiltrado = self.dfContasBancarias[ (self.dfContasBancarias['codigo_agencia'] == int(agencia)) & (self.dfContasBancarias['conta_e_digito'] == conta) ]
    #     if dfFiltrado.empty:
    #         resultado = f"Os campos AGENCIA e CONTA_CORRENTE não parecem corretos para esse contrato ({agencia}, {conta})"
        return resultado

    def check_full_dates(self, index):
        resultado = ''
        for campo in self.modelo.datasCompletas:
            if campo in self.df.columns:
                valor = self.df.at[index, campo]
                if not pd.isnull(valor):
                    padrao = re.compile(r'^\d{4}-\d{2}-\d{2}$')
                    if not re.match(padrao, str(valor)):
                        resultado += ', ' + f"{campo} possui formato invalido {valor}"
        return resultado

    def check_short_dates(self, index):
        resultado = ''
        for campo in self.modelo.datasAbreviadas:
            if campo in self.df.columns:
                valor = self.df.at[index, campo]
                if not pd.isnull(valor):
                    padrao = re.compile(r'^\d{4}-\d{2}$')
                    if not re.match(padrao, str(valor)):
                        resultado += ', ' + f"{campo} possui formato invalido {valor}"
        return resultado
    
    def check_pdf(self, nome_imagem):
        if pd.isna(nome_imagem):
            return "Campo DESCRIÇÃO não preenchido"

    def check_cpf(self, index, campo = None):
        resultado = ''
        if not campo:
            campo = 'CPF'
        valor = self.df.at[index, campo]
        if not pd.isnull(valor):
            if not cpfcnpj.validate(valor):
                resultado += ', ' + f"CPF possui formato invalido {valor}"
        return resultado
    
    def check_cnpj_cpf(self, index):
        resultado = ''
        if not pd.isnull(self.df.at[index, 'CNPJ_CPF']):
            resultado += self.check_cpf(index, 'CNPJ_CPF')
        if not pd.isnull(self.df.at[index, 'CNPJ_CPF']):
            resultado += self.check_cnpj(index, 'CNPJ_CPF')
        return resultado

    def check_cnpj(self, index, campo = None):
        resultado = ''
        if not campo:
            campo = 'CNPJ'
        valor = self.df.at[index, campo]
        if not pd.isnull(valor):
            if not cpfcnpj.validate(valor):
                resultado += ', ' + f"CNPJ possui formato invalido {valor}"
        return resultado
    
    def check_email(self, index):
        resultado = ''
        valor = self.df.at[index, 'EMAIL']
        if not pd.isnull(valor):
            padrao = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            if not re.match(padrao, str(valor)):
                resultado += ', ' + f"EMAIL possui formato invalido {valor}"
        return resultado

    def check_currency_values_br(self, index):
        resultado = ''
        for campo in self.modelo.camposMonetarios:
            if campo in self.df.columns:
                valor = self.df.at[index, campo]
                if not pd.isnull(valor):
                    padrao = re.compile(r'\d+(\.\d{3})*(,\d{1,2})?')
                    if not re.fullmatch(padrao, str(valor)):
                        resultado += ', ' + f"{campo} possui formato invalido {valor}"
        return resultado  
        
    def check_chars_len(self, index):
        resultado = ''
        for key, value in self.modelo.limitesTamanho.items():
            if key in self.df.columns:
                valor = self.df.at[index, key]
                if not pd.isnull(valor):
                    if len(str(valor)) > value:
                        resultado += ', ' + f"O dado inserido na coluna {key} possui tamanho maior que {value}"
        return resultado
    
    @staticmethod
    def check_numero_documento(numdoc):
        if not numdoc or numdoc.strip() == '':
            return ''

        numdoc = numdoc.strip()
        if re.fullmatch(r'[a-zA-Z0-9\sà-üÀ-ÜçÇéÉãÃõÕôÔîÎûÛ_\-\/\.]+', numdoc):
            return numdoc

        raise BaseError(
            f"O Número do Documento da despesa é inválido. Reporte ao desenvolvedor e pare a execução. {numdoc}")

    @staticmethod
    def str_to_us_str_date(data) -> str:
        match = re.search(r'\d{2}/\d{2}/\d{4}', data)
        if match:
            data_brasileira = match.group(0)
            data = datetime.datetime.strptime(data_brasileira, '%d/%m/%Y').strftime('%Y-%m-%d')
        return data
    
    @staticmethod
    def check_and_format_cpf(cpf):
        if not cpf or cpf.strip() == '':
            return ''
        if '*' in cpf:
            raise BaseError(f"O CPF da despesa está vindo com valores **** Reporte ao desenvolvedor e pare a execução. {cpf}")
        if cpfcnpj.validate(cpf.strip()):
            cpf_numerico = re.sub(r'[.\-\/\\]', '', cpf.strip())
            return f"{cpf_numerico[:3]}.{cpf_numerico[3:6]}.{cpf_numerico[6:9]}-{cpf_numerico[9:]}"

        raise BaseError(f"O CPF da despesa é inválido. {cpf}")

    @staticmethod
    def check_and_format_cnpj(cnpj):
        if not cnpj or cnpj.strip() == '':
            return ''
        if '*' in cnpj:
            raise BaseError(f"O CNPJ da despesa está vindo com valores **** Reporte ao desenvolvedor e pare a execução. {cnpj}")
        if cpfcnpj.validate(cnpj.strip()):
            cnpj_numerico = re.sub(r'[.\-\/\\]', '', cnpj.strip())
            return f"{cnpj_numerico[:2]}.{cnpj_numerico[2:5]}.{cnpj_numerico[5:8]}/{cnpj_numerico[8:12]}-{cnpj_numerico[12:]}"

        raise BaseError(f"O CPF da despesa é inválido. {cnpj}")

    @staticmethod
    def format_monetary_value(valor):
        if type(valor) == float:
            return valor

        if type(valor) == str:
            valor = valor.replace(',','.')
            valorFatiado = valor.split('.')
            if len(valorFatiado) > 1:
                return float( ''.join(valorFatiado[:-1]) + '.' + valorFatiado[-1]) 
            return float(valorFatiado[0])
        return valor

    @staticmethod
    def check_and_format_nome(nome): 
        if nome == None:
            return ""

        if not type(nome) == str:
            raise BaseError(f"O NOME da pessoa física não é uma string. {nome}")
        
        if nome == '':
            return nome
            
        if len(nome.strip()) > 100:
            raise BaseError(f"O NOME da pessoa física é muito grande (max 100). {nome}")

        if not re.fullmatch(r'[a-zA-Z0-9\sà-üÀ-ÜçÇéÉãÃõÕôÔîÎûÛ]+', nome.strip()):
            raise BaseError(f"O NOME da pessoa possui caracteres inválidos. {nome}")
        
        return nome.strip()#.upper()

    @staticmethod
    def check_and_format_razaosocial(razao):
        if not type(razao) == str:
            raise BaseError(f"A razaosocial da pessoa jurídica não é uma string. {razao}")

        if razao == '':
            return razao

        if len(razao.strip()) > 100:
            raise BaseError(f"A razaosocial da pessoa jurídica é muito grande (max 100). {razao}")

        if not re.fullmatch(r'[a-zA-Z0-9\sà-üÀ-ÜçÇéÉãÃõÕôÔîÎûÛ\.,\-_&/\()\?%]+', razao.strip()):
            raise BaseError(f"A razaosocial da pessoa possui caracteres inválidos. {razao}")
        
        return razao.strip()#.upper()

    def load_bank_account_by_contract_id(self):
        self.dfContasBancarias = pd.DataFrame()
        url = self.base_url + '/bankAccount/server/bankAccountServices/getBankAccountByContractId'
        try:
            requisicao = requests.post(url, json=str(self.id_contrato), cookies={"osinfo":f"{st.secrets['cookie']}"})
            requisicao.raise_for_status()
            self.dfContasBancarias = pd.DataFrame(data=requisicao.json())
            self.dfContasBancarias['conta_e_digito'] = [f"{x}{y}" for x,y in zip(self.dfContasBancarias['codigo_cc'], self.dfContasBancarias['digito_cc']) ]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro ao obter lista de tipos de documentos: {e}")  

    def load_unit_list_by_os_contract_unit_type(self):
        self.dfUnidades = pd.DataFrame()
        url = self.base_url + '/common/unit/server/unitServicesOld/getUnitsListByOsContractUnitType'
        try:
            requisicao = requests.post(url, json={"cod_unidade":"","id_contrato":str(self.id_contrato),"sigla_tipo":""}, cookies={"osinfo":f"{st.secrets['cookie']}"})
            requisicao.raise_for_status()
            self.dfUnidades = pd.DataFrame(data=requisicao.json())
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro ao obter lista de tipos de documentos: {e}")

    def load_providers_list(self):
        self.dfFornecedores = pd.DataFrame()
        with open('./data/providersList.json', encoding='utf-8') as arqFornecedores:
            self.dfFornecedores = pd.DataFrame(json.load(arqFornecedores))

    def load_contract_list(self):
        self.dfContratos = pd.DataFrame()
        with open('./data/getContractsList.json', encoding='utf-8') as arqContratos:
            self.dfContratos = pd.DataFrame(json.load(arqContratos))
            if 'num_contrato' not in self.dfContratos.columns:
                raise Exception("A coluna 'num_contrato' não foi encontrada na resposta da API.")

    def load_expense_type_list(self):
        self.dfCodigosDespesas = pd.DataFrame()
        with open('./data/getExpenseTypesList.json', encoding='utf-8') as getExpenseTypesList:
            self.dfCodigosDespesas = pd.DataFrame(json.load(getExpenseTypesList))

    def load_expenditures_list(self):
        self.dfRubricas = pd.DataFrame()
        with open('./data/getExpendituresList.json', encoding='utf-8') as getExpendituresList:
            self.dfRubricas = pd.DataFrame(json.load(getExpendituresList))

    def load_document_type_list(self):
        self.dfTiposDocumentos = pd.DataFrame()
        with open('./data/getDocumentTypesList.json', encoding='utf-8') as getDocumentTypesList:
            self.dfTiposDocumentos = pd.DataFrame(json.load(getDocumentTypesList))