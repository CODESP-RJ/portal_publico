LISTA_MODULOS = ['despesas', 'contratosdeterceiros', 'receitas', 'benspatrimoniados', 'saldos', 'itensdenotafiscal']

LISTA_ACOES = ['alteracao', 'exclusao', 'inclusao']

LISTA_ATRIBUTOS_SALDOS = [
    'valoremcontacorrente', 'aplicacaofinanceira', 'provisao', 'valoremespecie'
]

LISTA_ATRIBUTOS_DESPESAS = [
    'valorpago', 'valor', 'valordodocumento', 'rubrica', 'descricao', 'contacorrente', 'unidade',
    'despesa', 'imagem', 'linha', 'codigobancario', 'numerododocumento', 'cnpj', 'razaosocial',
    'datadeemissao', 'tipodedocumento', 'cpf', 'nome', 'datadevencimento', 'datadepagamento', 'datadeapuracao'
]

LISTA_ATRIBUTOS_CONTRATOS_DE_TERCEIROS = [
    'nomedoarquivo', 'servico', 'unidade', 'vigencia', 'valormes', 'razaosocial',
    'cnpj', 'cpf', 'nome', 'mesinicio', 'mesfim', 'anoinicio', 'anofim', 'contrato'
]

LISTA_ATRIBUTOS_BENS_PATRIMONIADOS = [
    'nomearquivoimagem', 'vidautil', 'vinculacao', 'setordestino', 'notafiscal', 'descricao', 'tipo',
    'controle', 'razaosocial', 'cnpj', 'quantidade', 'valor', 'unidade'
]

LISTA_ATRIBUTOS_ITENS_DE_NOTA_FISCAL = [
    'numerodanotafiscal', 'codigodomaterial', 'descricao', 'unidadedemedida', 'quantidade',
    'valorunitario', 'valortotal', 'mesdereferencia', 'anodereferencia','fornecedor', 'observacao'
]

LISTA_ATRIBUTOS_RECEITAS = [
    'contratodegestaopartefixa', 'repassecontratodegestaopartevariavel1',
    'repassecontratodegestaopartevariavel2', 'repassecontratodegestaopartevariavel3',
    'termoaditivoadicionalcusteio', 'termoaditivoadicionalinvestimento',
    'resultadodeaplicacaofinanceira', 'estornodedespesas',
    'obtencaoderecursosexternos', 'retornodeemprestimorealizadoaoutrocontrato', 'emprestimotomadodeoutrocontrato',
    'transferenciasentrecontasdeprovisionamentoeexecucao',
    'transferenciadeprovisionamentodecolaboradoresoriundosdeoutrocontratoeouunidade'
]

MAPPING_SALDOS = {
    'valoremcontacorrente': 'bankAccountValue',
    'aplicacaofinanceira': 'investmentValue',
    'provisao': 'provisioningValue',
    'valoremespecie': 'cashValue'
}

MAPPING_RECEITAS = {
    'contratodegestaopartefixa': 'budgetMngtFixedValue',
    'repassecontratodegestaopartevariavel1': 'budgetMngtVariable1Value',
    'repassecontratodegestaopartevariavel2': 'budgetMngtVariable2Value',
    'repassecontratodegestaopartevariavel3': 'budgetMngtVariable3Value',
    'termoaditivoadicionalcusteio': 'budgetAddCustTAValue',
    'termoaditivoadicionalinvestimento': 'budgetAddInvesTAValue',
    'resultadodeaplicacaofinanceira': 'investmentsValue',
    'estornodedespesas': 'expensesReverseValue',
    'obtencaoderecursosexternos': 'externalResourcesValue',
    'retornodeemprestimorealizadoaoutrocontrato': 'loanReverseValue',
    'emprestimotomadodeoutrocontrato': 'loanAnotherContractValue',
    'transferenciasentrecontasdeprovisionamentoeexecucao': 'transferAccountContractExecValue',
    'transferenciadeprovisionamentodecolaboradoresoriundosdeoutrocontratoeouunidade': 'transferResourceAnotherContractValue'
}

MAPPING_BENS_PATRIMONIADOS = {
    'tipo': 'id_bem_tipo',
    'descricao': 'descricao',
    'notafiscal': 'nf',
    'controle': 'num_controle',
    'vidautil': 'vida_util',
    'vinculacao': 'vinculacao',
    'setordestino': 'setor_destino',
    'nomearquivoimagem': 'img_nf',
    'razaosocial': 'fornecedor',
    'cnpj': 'cnpj',
    'quantidade': 'quantidade',
    'valor': 'valor',
    'unidade': 'cod_unidade',
}

MAPPING_ITENS_DE_NOTA_FISCAL = {
    'codigo': 'itnf_cd_item',
    'descricao': 'itnf_ds_item',
    'numerodanotafiscal': 'itnf_num_documento',
    'unidadedemedida': 'itnf_unidade_medida',
    'observacao': 'itnf_observacao',
    'quantidade': 'itnf_quantidade',
    'valorunitario': 'itnf_valor_unitario',
    'valortotal': 'itnf_valor_total',
    'fornecedor': 'itnf_sq_fornecedor',
    'codigodomaterial': 'itnf_cd_item',
    'codigodoservico': 'itnf_cd_item',
}

MAPPING_CONTRATOS_TERCEIROS = {
    'unidade': 'cod_unidade',
    'cnpj': 'cnpj',
    'cpf': 'cnpj',
    'nome': 'razao_social',
    'razaosocial': 'razao_social',
    'vigencia': 'vigencia',
    'valormes': 'valor_mes',
    'nomedoarquivo': 'imagem_contrato',
    'mesinicio': 'contrato_mes_inicio',
    'anoinicio': 'contrato_ano_inicio',
    'mesfim': 'contrato_mes_fim',
    'anofim': 'contrato_ano_fim',
    'servico': 'servico',
    'contrato': 'numeroContrato'
}

MAPPING_DESPESAS = {
    'descricao': "descricao",
    'unidade': "cod_unidade",
    'razaosocial': "razao",
    'cnpj': "cnpj",
    'nome': "nome",
    'cpf': "cpf",
    'despesa': "id_despesa",
    'rubrica': "id_rubrica",
    'tipodedocumento': "id_tipo_documento",
    'valordodocumento': "valor_documento",
    'valorpago': "valor_pago",
    'contacorrente': "id_conta_bancaria",
    'identificadorbancario': "cod_bancario",
    'codigobancario': 'cod_bancario',
    'parcelapaga': "pmt_mes",
    'numerodeparcelas': "pmt_total",
    'datadevencimento': "data_vencimento",
    'datadeemissao': "data_emissao",
    'datadepagamento': "data_pagamento",
    'datadeapuracao': "data_apuracao",
    'numerododocumento': "num_documento",
    'serie': 'serie',
    'codigofiscal': 'codigo_fiscal',
    'anomesreferencia': 'anomesreferencia'
}

COMMOM_FIELDS_DESPESAS = [
    'cod_unidade', 'cnpj', 'razao', 'descricao', 'data_emissao',
    'data_vencimento', 'data_pagamento', 'data_apuracao', 'valor_documento',
    'valor_pago', 'id_rubrica', 'pmt_mes', 'pmt_total', 'num_documento', 'serie'
]

MAPPING_EXPORT_DESPESAS = {
    'Num_Seq': "id_documento",
    'Descricao': "descricao",
    'unidade': "cod_unidade",
    'Razao': "razao",
    'Cnpj': "cnpj",
    'Nome': "nome",
    'Cpf': "cpf",
    'Despesa': "id_despesa",
    'Rubrica': "id_rubrica",
    'Tipo_Documento': "id_tipo_documento",
    'Valor_Documento': "valor_documento",
    'Valor_Pago': "valor_pago",
    'Conta_Corrente': "id_conta_bancaria",
    'Cod_Bancario': "cod_bancario",
    'Pmt_Mes': "pmt_mes",
    'Pmt_Total': "pmt_total",
    'Data_Vencimento': "data_vencimento",
    'Data_Emissao': "data_emissao",
    'Data_Pagamento': "data_pagamento",
    'Data_Apuracao': "data_apuracao",
    'Num_Documento': "num_documento",
    'Serie': 'serie',
    'Ano_Mes_Ref': 'anomesreferencia'
}