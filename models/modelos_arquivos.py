class Cabecalho:
    def __init__(self, modulo = None, tipo = None):
        if not modulo or not tipo:
            raise Exception('Os parametros modulo e tipo são obrigatórios ao instanciar um Modelo de Arquivo')

        self.modulo = modulo
        self.tipo = tipo

        self.cabecalho_str = ''
        self.cabecalho = []
        self.datas_abreviadas = []
        self.datas_completas = []
        self.campos_obrigatorios = []
        self.campos_monetarios = []
        self.limites_tamanho = {}

        if modulo == 'despesas':
            self.modulo_despesas()
        elif modulo == 'bens_patrimoniados':
            self.modulo_bens_patrimoniados()
        elif modulo == 'contratos_terceiros':
            self.modulo_contratos_terceiros()
        elif modulo == 'saldos':
            self.modulo_saldos()
        elif modulo == 'fornecedores':
            self.modulo_fornecedores()
        elif modulo == 'itens_nota_fiscal':
            self.modulo_itens_nota_fiscal()
        elif modulo == 'receitas':
            self.modulo_receitas()
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

    def modulo_despesas(self):
        self.cabecalho_str = 'COD_OS;COD_UNIDADE;COD_CONTRATO;ANO_MES_REF;TIPO;CODIGO;CNPJ;RAZAO;CPF;NOME;NUM_DOCUMENTO;SERIE;DESCRICAO;DATA_EMISSAO;DATA_VENCIMENTO;DATA_PAGAMENTO;DATA_APURACAO;VALOR_DOCUMENTO;VALOR_PAGO;DESPESA;RUBRICA;BANCO;AGENCIA;CONTA_CORRENTE;PMT_PAGA;QTDE_PMT;IDENT_BANCARIO;FLAG_JUSTIFICATIVA'
        self.cabecalho = Cabecalho.trata_cabecalho(self.cabecalho_str)
        self.datas_abreviadas = []
        self.datas_completas = ['DATA_EMISSAO', 'DATA_VENCIMENTO', 'DATA_PAGAMENTO', 'DATA_APURACAO', 'DATA_EMISSAO', 'DATA_VENCIMENTO', 'DATA_PAGAMENTO', 'DATA_APURACAO']
        self.campos_obrigatorios = ["COD_OS", "COD_UNIDADE", "COD_CONTRATO", "ANO_MES_REF", "TIPO", "DESCRICAO", "DATA_VENCIMENTO", "DATA_PAGAMENTO", "DATA_APURACAO",
                                    "VALOR_DOCUMENTO", "VALOR_PAGO", "DESPESA", "RUBRICA", "BANCO", "AGENCIA", "CONTA_CORRENTE", "PMT_PAGA", "QTDE_PMT", "IDENT_BANCARIO", "FLAG_JUSTIFICATIVA"]
        self.campos_monetarios = ['VALOR_DOCUMENTO', 'VALOR_PAGO', 'VALOR_DOCUMENTO', 'VALOR_PAGO']
        self.limites_tamanho = {"RAZAO" : 100, "NOME" : 100, "DESCRICAO" : 150, "NUM_DOCUMENTO" : 20, "SERIE" : 3, "DESPESA" : 50, "IDENT_BANCARIO" : 100}

    def modulo_bens_patrimoniados(self):
        self.cabecalho_str = 'COD_OS;COD_UNIDADE;COD_CONTRATO;ANO_MES_REF;NUM_CONTROLE_OS;NUM_CONTROLE_GOV;COD_TIPO;BEM_TIPO;DESCRICAO_NF;CNPJ;FORNECEDOR;QUANTIDADE;NF;DATA_AQUISICAO;VIDA_UTIL;VALOR;VINCULACAO;SETOR_DESTINO;IMG_NF'
        self.cabecalho = Cabecalho.trata_cabecalho(self.cabecalho_str)
        self.datas_abreviadas = ['ANO_MES_REF']
        self.datas_completas = ['DATA_AQUISICAO']
        self.campos_obrigatorios = ["COD_OS", "COD_UNIDADE", "COD_CONTRATO", "ANO_MES_REF", "NUM_CONTROLE_OS", "COD_TIPO", "BEM_TIPO", "DESCRICAO_NF", "CNPJ", "FORNECEDOR", "QUANTIDADE", "NF", "DATA_AQUISICAO", "VIDA_UTIL", "VALOR", "VINCULACAO", "IMG_NF"]
        self.campos_monetarios = ['VALOR']
        self.limites_tamanho =  {"DESCRICAO_NF" : 255, "FORNECEDOR" : 255, "NF" : 20, "VINCULACAO" : 255, "SETOR_DESTINO" : 100}

    def modulo_saldos(self):
        self.cabecalho_str = 'COD_OS;COD_UNIDADE;COD_CONTRATO;ANO_MES_REF;BANCO;AGENCIA;CONTA_CORRENTE;VL_CONTA_CORRENTE;VL_APL_FINANCEIRA;VL_CONTA_PROVISAO;VL_EM_ESPECIE;EXTRATO'
        self.cabecalho = Cabecalho.trata_cabecalho(self.cabecalho_str)
        self.datas_abreviadas = ['ANO_MES_REF']
        self.datas_completas = []
        self.campos_obrigatorios = ["COD_OS", "COD_UNIDADE", "COD_CONTRATO", "ANO_MES_REF", "BANCO", "AGENCIA", "CONTA_CORRENTE", "VL_CONTA_CORRENTE", "VL_APL_FINANCEIRA", "VL_CONTA_PROVISAO", "VL_EM_ESPECIE", "EXTRATO"]
        self.campos_monetarios = ['VL_CONTA_CORRENTE', 'VL_APL_FINANCEIRA', 'VL_CONTA_PROVISAO', 'VL_EM_ESPECIE']
        self.limites_tamanho = {}

    def modulo_contratos_terceiros(self):
        self.cabecalho_str = 'COD_OS;COD_UNIDADE;COD_CONTRATO;RAZAO_SOCIAL;CNPJ;SERVICO;VALOR_MES;VIGENCIA;CONTRATO_ANO_MES_INICIO;CONTRATO_ANO_MES_FIM;REF_TRI;REF_ANO_MES;IMG_CONTRATO'
        self.cabecalho =  Cabecalho.trata_cabecalho(self.cabecalho_str)
        self.datas_abreviadas = ['CONTRATO_ANO_MES_INICIO', 'CONTRATO_ANO_MES_FIM', 'REF_TRI']
        self.datas_completas = ['REF_ANO_MES']
        self.campos_obrigatorios = ["COD_OS", "COD_UNIDADE", "COD_CONTRATO", "RAZAO_SOCIAL", "CNPJ", "SERVICO", "VALOR_MES", "VIGENCIA", "CONTRATO_ANO_MES_INICIO", "CONTRATO_ANO_MES_FIM", "REF_TRI", "REF_ANO_MES", "IMG_CONTRATO"]
        self.campos_monetarios = ['VALOR_MES']
        self.limites_tamanho = {"RAZAO_SOCIAL" : 100}

    def modulo_fornecedores(self):
        self.cabecalho_str = 'CNPJ_CPF;NOME_FORNECEDOR;TIPO;CONTATO;ENDERECO;NUMERO;COMPLEMENTO;CEP;BAIRRO;MUNICIPIO;UF;REFERENCIA;FONE_1;RAMAL_1;FONE_2;RAMAL_2;FAX;EMAIL'
        self.cabecalho =  Cabecalho.trata_cabecalho(self.cabecalho_str)
        self.datas_abreviadas = []
        self.datas_completas = []
        self.campos_obrigatorios = ["CNPJ_CPF", "NOME_FORNECEDOR", "TIPO", "ENDERECO", "NUMERO", "CEP", "BAIRRO"]
        self.campos_monetarios = []
        self.limites_tamanho = { }

    def modulo_itens_nota_fiscal(self):
        self.cabecalho_str = 'NUM_OS;COD_MAT_SERV;DESC_MAT_SERV;UNID_MED;PREC_UNIT;QTD;VLR_TOT_ITEM;NF;CNPJ_FORN;MAT_OU_SERV;MES_ANO;OBS'
        self.cabecalho =  Cabecalho.trata_cabecalho(self.cabecalho_str)
        self.datas_abreviadas = ["MES_ANO"]
        self.datas_completas = []
        self.campos_obrigatorios = ["NUM_OS", "COD_MAT_SERV", "DESC_MAT_SERV", "UNID_MED", "PREC_UNIT", "QTD", "VLR_TOT_ITEM", "NF", "CNPJ_FORN", "MAT_OU_SERV", "MES_ANO"]
        self.campos_monetarios = ["PREC_UNIT", "VLR_TOT_ITEM"]
        self.limites_tamanho = {"DESC_MAT_SERV" : 700, "UNID_MED" : 50, "NF" : 20, "OBS" : 250, "COD_MAT_SERV" : 12}

    def modulo_receitas(self):
        self.cabecalho_str = 'D;COD_OS;COD_UNIDADE;COD_CONTRATO;ANO_MES_REF;BANCO;AGENCIA;CONTA_CORRENTE;REC_CONT_GES_FIXA;REC_CONT_GES_VARIAVEL;REC_TA_ADIC_CUSTEIO;REC_TA_ADIC_INVEST;REC_APLIC_FINANCEIRA;REC_REEMB_DESPESAS;REC_RECURSOS_EXTERNOS;REC_REC_EXTRAS;REC_OUTRAS_RECEITAS;REC_CONT_GES_VARIAVEL_2;REC_CONT_GES_VARIAVEL_3;REC_REP_SUS_AIH;REC_REP_SUS_AMB;REC_REP_SUS_INTEGRASUS'
        self.cabecalho =  Cabecalho.trata_cabecalho(self.cabecalho_str)
        self.datas_abreviadas = ['ANO_MES_REF']
        self.datas_completas = []
        self.campos_obrigatorios = ["D", "COD_OS", "COD_UNIDADE", "COD_CONTRATO", "ANO_MES_REF", "BANCO", "AGENCIA", "CONTA_CORRENTE", "REC_CONT_GES_FIXA", "REC_CONT_GES_VARIAVEL", "REC_TA_ADIC_CUSTEIO", "REC_TA_ADIC_INVEST", "REC_APLIC_FINANCEIRA", "REC_REEMB_DESPESAS", "REC_RECURSOS_EXTERNOS", "REC_REC_EXTRAS", "REC_OUTRAS_RECEITAS", "REC_CONT_GES_VARIAVEL_2", "REC_CONT_GES_VARIAVEL_3", "REC_REP_SUS_AIH", "REC_REP_SUS_AMB", "REC_REP_SUS_INTEGRASUS"]
        self.campos_monetarios = ['REC_CONT_GES_FIXA', 'REC_CONT_GES_VARIAVEL', 'REC_TA_ADIC_CUSTEIO', 'REC_TA_ADIC_INVEST', 'REC_APLIC_FINANCEIRA', 'REC_REEMB_DESPESAS', 'REC_RECURSOS_EXTERNOS', 'REC_REC_EXTRAS', 'REC_OUTRAS_RECEITAS', 'REC_CONT_GES_VARIAVEL_2', 'REC_CONT_GES_VARIAVEL_3', 'REC_REP_SUS_AIH', 'REC_REP_SUS_AMB', 'REC_REP_SUS_INTEGRASUS']
        self.limites_tamanho = { }
    
    @staticmethod
    def trata_cabecalho(cabecalho):
        cabecalhoTratado = cabecalho
        cabecalhoTratado = cabecalhoTratado.replace(" ","").strip('\r\n').upper()
        cabecalhoTratado = cabecalhoTratado.split(";")
        return cabecalhoTratado

    @staticmethod
    def get_os_list_type():
        return ['COD_OS', 'ORGANIZACAO', 'NUM_OS', 'CNPJ_CPF']