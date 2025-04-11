class Cabecalho:
    def __init__(self, modulo = None, tipo = None):
        if not modulo or not tipo:
            raise Exception('Os parametros modulo e tipo são obrigatórios ao instanciar um Modelo de Arquivo')
        
        self.modulo = modulo
        self.tipo = tipo

        self.cabecalhoStr = ''
        self.cabecalho = []
        self.datasAbreviadas = []
        self.datasCompletas = []
        self.camposObrigatorios = []
        self.camposMonetarios = []
        self.limitesTamanho = {}

        if modulo == 'despesas' and tipo == 'importacao':
            self.modulo_despesas_tipo_importacao()
        elif modulo == 'bens_patrimoniados' and tipo == 'importacao':
            self.modulo_bens_patrimoniados_tipo_importacao()
        elif modulo == 'contratos_terceiros' and tipo == 'importacao':
            self.modulo_contratos_terceiros_tipo_importacao()
        elif modulo == 'saldos' and tipo == 'importacao':
            self.modulo_saldos_tipo_importacao()
        elif modulo == 'fornecedores' and tipo == 'importacao':
            self.modulo_fornecedores_tipo_importacao()
        elif modulo == 'itens_nota_fiscal' and tipo == 'importacao':
            self.modulo_itens_nota_fiscal_tipo_importacao()
        elif modulo == 'receitas' and tipo == 'importacao':
            self.modulo_receitas_tipo_importacao()
        else:
            raise Exception('Modulo e/ou Tipo de Arquivo não implementado')        

    def retorna_cabecalho(self):
        if not self.cabecalho:
            self.cabecalho = self.trata_cabecalho(self.cabecalho_str)
        return self.cabecalho
    
    def contem_cabecalho(self, cabecalhoModelo, cabecalhoArquivo):
        todosContidos = all(item in cabecalhoArquivo for item in cabecalhoModelo)
        if todosContidos:
            return True
        else:
            return False

    def modulo_despesas_tipo_importacao(self):
        self.cabecalhoStr = 'COD_OS;COD_UNIDADE;COD_CONTRATO;ANO_MES_REF;TIPO;CODIGO;CNPJ;RAZAO;CPF;NOME;NUM_DOCUMENTO;SERIE;DESCRICAO;DATA_EMISSAO;DATA_VENCIMENTO;DATA_PAGAMENTO;DATA_APURACAO;VALOR_DOCUMENTO;VALOR_PAGO;DESPESA;RUBRICA;BANCO;AGENCIA;CONTA_CORRENTE;PMT_PAGA;QTDE_PMT;IDENT_BANCARIO;FLAG_JUSTIFICATIVA'
        self.cabecalho = Cabecalho.trata_cabecalho(self.cabecalhoStr)
        self.datasAbreviadas = []
        self.datasCompletas = ['DATA_EMISSAO','DATA_VENCIMENTO','DATA_PAGAMENTO','DATA_APURACAO','DATA_EMISSAO','DATA_VENCIMENTO','DATA_PAGAMENTO','DATA_APURACAO']
        self.camposObrigatorios = ["COD_OS", "COD_UNIDADE", "COD_CONTRATO", "ANO_MES_REF", "TIPO", "DESCRICAO", "DATA_VENCIMENTO", "DATA_PAGAMENTO", "DATA_APURACAO", 
                                    "VALOR_DOCUMENTO", "VALOR_PAGO", "DESPESA", "RUBRICA", "BANCO", "AGENCIA", "CONTA_CORRENTE", "PMT_PAGA", "QTDE_PMT", "IDENT_BANCARIO", "FLAG_JUSTIFICATIVA"]
        self.camposMonetarios = ['VALOR_DOCUMENTO','VALOR_PAGO','VALOR_DOCUMENTO','VALOR_PAGO']
        self.limitesTamanho = {"RAZAO" : 100, "NOME" : 100, "DESCRICAO" : 150, "NUM_DOCUMENTO" : 20, "SERIE" : 3, "DESPESA" : 50, "IDENT_BANCARIO" : 100}

    def modulo_bens_patrimoniados_tipo_importacao(self):
        self.cabecalhoStr = 'COD_OS;COD_UNIDADE;COD_CONTRATO;ANO_MES_REF;NUM_CONTROLE_OS;NUM_CONTROLE_GOV;COD_TIPO;BEM_TIPO;DESCRICAO_NF;CNPJ;FORNECEDOR;QUANTIDADE;NF;DATA_AQUISICAO;VIDA_UTIL;VALOR;VINCULACAO;SETOR_DESTINO;IMG_NF'
        self.cabecalho = Cabecalho.trata_cabecalho(self.cabecalhoStr)
        self.datasAbreviadas = ['ANO_MES_REF']
        self.datasCompletas = ['DATA_AQUISICAO']
        self.camposObrigatorios = [ "COD_OS", "COD_UNIDADE", "COD_CONTRATO", "ANO_MES_REF", "NUM_CONTROLE_OS", "COD_TIPO", "BEM_TIPO", "DESCRICAO_NF", "CNPJ", "FORNECEDOR", "QUANTIDADE", "NF", "DATA_AQUISICAO", "VIDA_UTIL", "VALOR", "VINCULACAO", "IMG_NF"]
        self.camposMonetarios = ['VALOR']
        self.limitesTamanho =  {"DESCRICAO_NF" : 255, "FORNECEDOR" : 255, "NF" : 20, "VINCULACAO" : 255, "SETOR_DESTINO" : 100}

    def modulo_saldos_tipo_importacao(self):
        self.cabecalhoStr = 'COD_OS;COD_UNIDADE;COD_CONTRATO;ANO_MES_REF;BANCO;AGENCIA;CONTA_CORRENTE;VL_CONTA_CORRENTE;VL_APL_FINANCEIRA;VL_CONTA_PROVISAO;VL_EM_ESPECIE;EXTRATO'
        self.cabecalho = Cabecalho.trata_cabecalho(self.cabecalhoStr)
        self.datasAbreviadas = ['ANO_MES_REF']
        self.datasCompletas = []
        self.camposObrigatorios = [ "COD_OS", "COD_UNIDADE", "COD_CONTRATO", "ANO_MES_REF", "BANCO", "AGENCIA", "CONTA_CORRENTE", "VL_CONTA_CORRENTE", "VL_APL_FINANCEIRA", "VL_CONTA_PROVISAO", "VL_EM_ESPECIE", "EXTRATO"]
        self.camposMonetarios = ['VL_CONTA_CORRENTE','VL_APL_FINANCEIRA','VL_CONTA_PROVISAO','VL_EM_ESPECIE']
        self.limitesTamanho = {}

    def modulo_contratos_terceiros_tipo_importacao(self):
        self.cabecalhoStr = 'COD_OS;COD_UNIDADE;COD_CONTRATO;RAZAO_SOCIAL;CNPJ;SERVICO;VALOR_MES;VIGENCIA;CONTRATO_ANO_MES_INICIO;CONTRATO_ANO_MES_FIM;REF_TRI;REF_ANO_MES;IMG_CONTRATO'
        self.cabecalho =  Cabecalho.trata_cabecalho(self.cabecalhoStr)
        self.datasAbreviadas = ['CONTRATO_ANO_MES_INICIO','CONTRATO_ANO_MES_FIM','REF_TRI']
        self.datasCompletas = ['REF_ANO_MES']
        self.camposObrigatorios = [ "COD_OS",  "COD_UNIDADE",  "COD_CONTRATO",  "RAZAO_SOCIAL",  "CNPJ",  "SERVICO",  "VALOR_MES",  "VIGENCIA",  "CONTRATO_ANO_MES_INICIO",  "CONTRATO_ANO_MES_FIM",  "REF_TRI",  "REF_ANO_MES",  "IMG_CONTRATO" ]
        self.camposMonetarios = ['VALOR_MES']
        self.limitesTamanho = { "RAZAO_SOCIAL" : 100 }

    def modulo_fornecedores_tipo_importacao(self):
        self.cabecalhoStr = 'CNPJ_CPF;NOME_FORNECEDOR;TIPO;CONTATO;ENDERECO;NUMERO;COMPLEMENTO;CEP;BAIRRO;MUNICIPIO;UF;REFERENCIA;FONE_1;RAMAL_1;FONE_2;RAMAL_2;FAX;EMAIL'
        self.cabecalho =  Cabecalho.trata_cabecalho(self.cabecalhoStr)
        self.datasAbreviadas = []
        self.datasCompletas = []
        self.camposObrigatorios = [ "CNPJ_CPF",  "NOME_FORNECEDOR",  "TIPO",  "ENDERECO",  "NUMERO",  "CEP",  "BAIRRO" ]
        self.camposMonetarios = []
        self.limitesTamanho = { }

    def modulo_itens_nota_fiscal_tipo_importacao(self):
        self.cabecalhoStr = 'NUM_OS;COD_MAT_SERV;DESC_MAT_SERV;UNID_MED;PREC_UNIT;QTD;VLR_TOT_ITEM;NF;CNPJ_FORN;MAT_OU_SERV;MES_ANO;OBS'
        self.cabecalho =  Cabecalho.trata_cabecalho(self.cabecalhoStr)
        self.datasAbreviadas = ["MES_ANO"]
        self.datasCompletas = []
        self.camposObrigatorios = ["NUM_OS","COD_MAT_SERV","DESC_MAT_SERV","UNID_MED","PREC_UNIT","QTD","VLR_TOT_ITEM","NF","CNPJ_FORN","MAT_OU_SERV","MES_ANO"]
        self.camposMonetarios = ["PREC_UNIT", "VLR_TOT_ITEM"]
        self.limitesTamanho = { "DESC_MAT_SERV" : 700, "UNID_MED" : 50, "NF" : 20, "OBS" : 250, "COD_MAT_SERV" : 12}

    def modulo_receitas_tipo_importacao(self):
        self.cabecalhoStr = 'D;COD_OS;COD_UNIDADE;COD_CONTRATO;ANO_MES_REF;BANCO;AGENCIA;CONTA_CORRENTE;REC_CONT_GES_FIXA;REC_CONT_GES_VARIAVEL;REC_TA_ADIC_CUSTEIO;REC_TA_ADIC_INVEST;REC_APLIC_FINANCEIRA;REC_REEMB_DESPESAS;REC_RECURSOS_EXTERNOS;REC_REC_EXTRAS;REC_OUTRAS_RECEITAS;REC_CONT_GES_VARIAVEL_2;REC_CONT_GES_VARIAVEL_3;REC_REP_SUS_AIH;REC_REP_SUS_AMB;REC_REP_SUS_INTEGRASUS'
        self.cabecalho =  Cabecalho.trata_cabecalho(self.cabecalhoStr)
        self.datasAbreviadas = ['ANO_MES_REF']
        self.datasCompletas = []
        self.camposObrigatorios = [ "D", "COD_OS",  "COD_UNIDADE",  "COD_CONTRATO",  "ANO_MES_REF",  "BANCO",  "AGENCIA",  "CONTA_CORRENTE",  "REC_CONT_GES_FIXA",  "REC_CONT_GES_VARIAVEL",  "REC_TA_ADIC_CUSTEIO",  "REC_TA_ADIC_INVEST",  "REC_APLIC_FINANCEIRA",  "REC_REEMB_DESPESAS",  "REC_RECURSOS_EXTERNOS",  "REC_REC_EXTRAS",  "REC_OUTRAS_RECEITAS",  "REC_CONT_GES_VARIAVEL_2",  "REC_CONT_GES_VARIAVEL_3",  "REC_REP_SUS_AIH",  "REC_REP_SUS_AMB",  "REC_REP_SUS_INTEGRASUS"]
        self.camposMonetarios = ['REC_CONT_GES_FIXA','REC_CONT_GES_VARIAVEL','REC_TA_ADIC_CUSTEIO','REC_TA_ADIC_INVEST','REC_APLIC_FINANCEIRA','REC_REEMB_DESPESAS','REC_RECURSOS_EXTERNOS','REC_REC_EXTRAS','REC_OUTRAS_RECEITAS','REC_CONT_GES_VARIAVEL_2','REC_CONT_GES_VARIAVEL_3','REC_REP_SUS_AIH','REC_REP_SUS_AMB','REC_REP_SUS_INTEGRASUS']
        self.limitesTamanho = { }     
    
    @staticmethod
    def trata_cabecalho(cabecalho):
        cabecalhoTratado = cabecalho
        cabecalhoTratado = cabecalhoTratado.replace(" ","").strip('\r\n').upper()
        cabecalhoTratado = cabecalhoTratado.split(";")
        return cabecalhoTratado

    @staticmethod
    def get_os_list_type():
        return ['COD_OS', 'ORGANIZACAO', 'NUM_OS', 'CNPJ_CPF']