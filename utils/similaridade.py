from difflib import SequenceMatcher

from models.common import (
    LISTA_MODULOS,
    LISTA_ACOES,
    LISTA_ATRIBUTOS_DESPESAS,
    LISTA_ATRIBUTOS_CONTRATOS_DE_TERCEIROS,
    LISTA_ATRIBUTOS_BENS_PATRIMONIADOS,
    LISTA_ATRIBUTOS_ITENS_DE_NOTA_FISCAL,
    LISTA_ATRIBUTOS_RECEITAS,
    LISTA_ATRIBUTOS_SALDOS
)

def calcular_similaridade(nova_palavra, tipo):
    """
    Calcula a similaridade entre a nova palavra e uma lista de palavras pré-definidas.

    Args:
        nova_palavra (str): Palavra a ser comparada.
        tipo (int): Tipo de lista (1 para módulos, 2 para atributos).

    Returns:
        str: Palavra mais similar da lista ou a própria novaPalavra se a similaridade for zero.
    """

    tipos = {
        'acao': LISTA_ACOES,
        'modulo': LISTA_MODULOS,
        'despesas': LISTA_ATRIBUTOS_DESPESAS,
        'benspatrimoniados': LISTA_ATRIBUTOS_BENS_PATRIMONIADOS,
        'contratosdeterceiros': LISTA_ATRIBUTOS_CONTRATOS_DE_TERCEIROS,
        'itensdenotafiscal': LISTA_ATRIBUTOS_ITENS_DE_NOTA_FISCAL,
        'receitas': LISTA_ATRIBUTOS_RECEITAS,
        'saldos': LISTA_ATRIBUTOS_SALDOS
    }

    lista = tipos[tipo]

    distancias = {}

    for palavra in lista:
        distancias[palavra] = SequenceMatcher(None, nova_palavra, palavra).ratio()

    maxi = max(distancias, key=distancias.get)

    return maxi if distancias[maxi] != 0.0 else nova_palavra
