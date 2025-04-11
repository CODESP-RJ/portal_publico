class Modulos:
    def __init__(self):
        self.Despesas = 'COD_OS;COD_UNIDADE;COD_CONTRATO;ANO_MES_REF;TIPO;CODIGO;CNPJ;RAZAO;CPF;NOME;NUM_DOCUMENTO;SERIE;DESCRICAO;DATA_EMISSAO;DATA_VENCIMENTO;DATA_PAGAMENTO;DATA_APURACAO;VALOR_DOCUMENTO;VALOR_PAGO;DESPESA;RUBRICA;BANCO;AGENCIA;CONTA_CORRENTE;PMT_PAGA;QTDE_PMT;IDENT_BANCARIO;FLAG_JUSTIFICATIVA'
        self.ContratosTerceiros = 'COD_OS;COD_UNIDADE;COD_CONTRATO;RAZAO_SOCIAL;CNPJ;SERVICO;VALOR_MES;VIGENCIA;CONTRATO_ANO_MES_INICIO;CONTRATO_ANO_MES_FIM;REF_TRI;REF_ANO_MES;IMG_CONTRATO'
        self.Saldos = 'COD_OS;COD_UNIDADE;COD_CONTRATO;ANO_MES_REF;BANCO;AGENCIA;CONTA_CORRENTE;VL_CONTA_CORRENTE;VL_APL_FINANCEIRA;VL_CONTA_PROVISAO;VL_EM_ESPECIE;EXTRATO'
        self.Bens = 'COD_OS;COD_UNIDADE;COD_CONTRATO;ANO_MES_REF;NUM_CONTROLE_OS;NUM_CONTROLE_GOV;COD_TIPO;BEM_TIPO;DESCRICAO_NF;CNPJ;FORNECEDOR;QUANTIDADE;NF;DATA_AQUISICAO;VIDA_UTIL;VALOR;VINCULACAO;SETOR_DESTINO;IMG_NF'
        self.Alteracao = ''
        self.cabecalhoDespesas = []
        self.datasCompletasDespesas = ['DATA_EMISSAO', 'DATA_VENCIMENTO', 'DATA_PAGAMENTO', 'DATA_APURACAO',
                                       'DATA_EMISSAO', 'DATA_VENCIMENTO', 'DATA_PAGAMENTO', 'DATA_APURACAO']
        self.camposMonetariosDespesas = ['VALOR_DOCUMENTO', 'VALOR_PAGO', 'VALOR_DOCUMENTO', 'VALOR_PAGO']
        self.cabecalhoContratosTerceiros = []
        self.datasAbreviadasContratosTerceiros = ['CONTRATO_ANO_MES_INICIO', 'CONTRATO_ANO_MES_FIM', 'REF_TRI']
        self.datasCompletasContratosTerceiros = ['REF_ANO_MES']
        self.camposMonetariosContratosTerceiros = ['VALOR_MES']
        self.datasAbreviadasSaldos = ['ANO_MES_REF']
        self.camposMonetariosSaldos = ['VL_CONTA_CORRENTE', 'VL_APL_FINANCEIRA', 'VL_CONTA_PROVISAO', 'VL_EM_ESPECIE']
        self.cabecalhoSaldos = []
        self.cabecalhoBens = []
        self.datasCompletasBens = ['DATA_AQUISICAO']
        self.datasAbreviadasBens = ['ANO_MES_REF']
        self.camposMonetariosBens = ['VALOR']
        self.datasCompletas = ['DATA_EMISSAO', 'DATA_VENCIMENTO', 'DATA_PAGAMENTO', 'DATA_APURACAO', 'DATA_DE_EMISSAO',
                               'DATA_DE_VENCIMENTO', 'DATA_DE_PAGAMENTO', 'DATA_DE_APURACAO', 'REF_TRI']
        self.datasAbreviadas = ['ANO_MES_REF', 'ANO_MES_DE_REFERENCIA', 'REF_ANO_MES', 'CONTRATO_ANO_MES_INICIO',
                                'CONTRATO_ANO_MES_FIM']
        self.documentosPDF = ['Descrição', 'Descricão', 'IMG_CONTRATO', 'EXTRATO', 'IMG_NF',
                              'Nome do Arquivo', 'Descricao', 'imagem_contrato', 'imagem']
        self.listaOS = ['COD_OS', 'ORGANIZACAO']

    def retorna_cabecalho_despesas(self):
        if not self.cabecalhoDespesas:
            self.cabecalhoDespesas = self.trata_cabecalho(self.Despesas)
        return self.cabecalhoDespesas

    def retorna_cabecalho_contratos_terceiros(self):
        if not self.cabecalhoContratosTerceiros:
            self.cabecalhoContratosTerceiros = self.trata_cabecalho(self.ContratosTerceiros)
        return self.cabecalhoContratosTerceiros

    def retorna_cabecalho_saldos(self):
        if not self.cabecalhoSaldos:
            self.cabecalhoSaldos = self.trata_cabecalho(self.Saldos)
        return self.cabecalhoSaldos

    def retorna_cabecalho_bens(self):
        if not self.cabecalhoBens:
            self.cabecalhoBens = self.trata_cabecalho(self.Bens)
        return self.cabecalhoBens

    def trata_cabecalho(self, cabecalho):
        cabecalhoTratado = cabecalho
        cabecalhoTratado = cabecalhoTratado.replace(" ", "").strip('\r\n').upper()
        cabecalhoTratado = cabecalhoTratado.split(";")
        return cabecalhoTratado

    def contem_cabecalho(self, cabecalhoModelo, cabecalhoArquivo):
        todosContidos = all(item in cabecalhoArquivo for item in cabecalhoModelo)
        if todosContidos:
            return True
        else:
            return False