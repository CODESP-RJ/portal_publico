import unicodedata
import re
import pandas as pd
from pycpfcnpj import cpfcnpj
from datetime import datetime

def verificar_formato_brasileiro(valor, casas_decimais=2):
    """
    Verifica se o valor está no formato brasileiro correto com casas decimais específicas
    - casas_decimais: 2 para VALOR TOTAL, 4 para VALOR UNITARIO
    """
    if pd.isna(valor) or valor is None:
        return True  # Considera válido se for vazio

    valor_str = str(valor).strip()

    # Padrão para formato brasileiro com decimais
    padrao_br_com_decimal = re.compile(r'^-?\d{1,3}(?:\.\d{3})*(?:,\d{' + str(casas_decimais) + '})$')
    padrao_br_sem_decimal = re.compile(r'^-?\d{1,3}(?:\.\d{3})*$')

    # Padrão para número simples sem separador de milhar
    padrao_simples_com_decimal = re.compile(r'^-?\d+(?:,\d{' + str(casas_decimais) + '})$')
    padrao_simples_sem_decimal = re.compile(r'^-?\d+$')

    return (bool(padrao_br_com_decimal.match(valor_str)) or
            bool(padrao_br_sem_decimal.match(valor_str)) or
            bool(padrao_simples_com_decimal.match(valor_str)) or
            bool(padrao_simples_sem_decimal.match(valor_str)))

def validar_data_brasileira(valor):
    """
    Verifica se a data está no formato DD/MM/YYYY
    """
    if pd.isna(valor) or valor is None:
        return True  # Considera válido se for vazio

    valor_str = str(valor).strip()

    try:
        # Tenta converter a string para datetime
        datetime.strptime(valor_str, '%d/%m/%Y')
        return True
    except ValueError:
        return False

def normalizar_atributos(df_original, df_atributos):
    print("Iniciando a normalização dos atributos...")

    # Padronizar colunas no df_original: remover espaços extras, preencher NaN, converter para minúsculas
    df_original['TIPO_MODULO'] = df_original['TIPO_MODULO'].fillna('').str.lower().str.replace(' ', '')
    df_original['ATRIBUTO'] = df_original['ATRIBUTO'].fillna('').str.lower().str.strip()

    for index, row in df_atributos.iterrows():

        # Remover espaços antes de comparar
        modulo_lower = row['MODULO'].lower().replace(' ', '')
        atributo_lower = row['ATRIBUTO'].lower().strip()
        similaridade_lower = row['SIMILARIDADE'].lower().strip()

        # Criar máscara booleana corrigida
        mask = (
            (df_original['TIPO_MODULO'] == modulo_lower)
        ) & (df_original['ATRIBUTO'] == atributo_lower)

        # Debugging: verificar valores do DataFrame original antes da alteração
        print("\nValores correspondentes antes da alteração:")
        print(df_original.loc[mask, ['TIPO_MODULO', 'ATRIBUTO']])

        # Aplicar alteração apenas se houver correspondências
        if not mask.any():
            print("⚠️ Nenhuma correspondência encontrada para essa linha! Verifique se os nomes batem exatamente.")
            continue

        # Substituir valores
        df_original.loc[mask, 'ATRIBUTO'] = similaridade_lower

        # Debugging: verificar valores do DataFrame após a alteração
        print("\nValores correspondentes após a alteração:")
        print(df_original.loc[mask, ['TIPO_MODULO', 'ATRIBUTO']])

    print("\n✅ Normalização concluída.")
    return df_original

def remover_acentos(texto):
    """
        Remove acentos de um texto.

        Args:
            texto (str): Texto a ser normalizado.

        Returns:
            str: Texto sem acentos.
    """
    try:
        nfkd_form = unicodedata.normalize('NFKD', texto)
        only_ascii = nfkd_form.encode('ASCII', 'ignore')
        return only_ascii.decode('ascii')

    except:
        return texto

def string_to_float(valor: str):
    """
        Esta função converte uma string que representa um número com pontos decimais em uma string formatada corretamente.

        Parâmetros:
        valor (str): A string que representa o número a ser convertido.

        Retorna:
        str: A string formatada corretamente.
    """
    valor = valor.replace(',', '.')

    valor_fatiado = valor.split('.')

    if len(valor_fatiado) > 1:
        to_string = ''.join(valor_fatiado[:-1]) + '.' + valor_fatiado[-1]

    else:
        to_string = valor_fatiado[0]

    return to_string

def adicionar_extensao_pdf(nome_arquivo):
    if not (nome_arquivo.endswith(".pdf") or nome_arquivo.endswith(".PDF")):
        nome_arquivo += ".pdf"
    return nome_arquivo


def formata_cnpj(cnpj: str) -> str:
    cnpj = cnpj.strip()
    if cpfcnpj.validate(cnpj):
        cnpj_numerico = re.sub(r'\D', '', cnpj)
        return f"{cnpj_numerico[:2]}.{cnpj_numerico[2:5]}.{cnpj_numerico[5:8]}/{cnpj_numerico[8:12]}-{cnpj_numerico[12:]}"
    else:
        return "inválido"


def formata_cpf(cpf: str) -> str:
    if isinstance(cpf, list):
        if len(cpf) > 0:
            cpf = str(cpf[0])
        else:
            return "invalido"
    cpf = str(cpf).strip()
    if cpfcnpj.validate(cpf):
        cpf_numerico = re.sub(r'[.\-\/\\]', '', cpf)
        return f"{cpf_numerico[:3]}.{cpf_numerico[3:6]}.{cpf_numerico[6:9]}-{cpf_numerico[9:]}"
    else:
        return "invalido"

def abrir_arquivo(caminho_arquivo: str):
    """
    Abre um arquivo CSV ou XLSX e carrega em um DataFrame.

    Args:
        caminho_arquivo (str): Caminho do arquivo CSV a ser carregado.

    Returns:
        pd.DataFrame: DataFrame contendo os dados do arquivo CSV.
    """
    df = None

    if caminho_arquivo.endswith('.xlsx'):
        df = pd.read_excel(caminho_arquivo)
    elif caminho_arquivo.endswith('.csv'):
        df = pd.read_csv(caminho_arquivo, sep=None, encoding="latin1", engine='python')

    return df

def padronizar_texto(df, fun=None):
    """
    Padroniza o texto em um DataFrame, removendo acentos, espaços extras e convertendo para minúsculas.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados a serem padronizados.

    Returns:
        pd.DataFrame: DataFrame padronizado.
    """

    if fun is None:
        for col in ['TIPO_MODULO', 'ATRIBUTO', 'ACAO']:
            if col in df.columns:
                df[col] = df[col].fillna('').astype(str).str.lower().str.strip()

        df = df.applymap(remover_acentos)

        if 'ATRIBUTO' in df.columns:
            df['ATRIBUTO'] = df['ATRIBUTO'].str.replace('_', '').str.replace('/', '').str.strip()

        return df
    else:
        df.columns = ['TIPO_MODULO', 'ANO_MES_REF', 'ACAO', 'ID', 'ATRIBUTO', 'NOVO_VALOR']

        df['TIPO_MODULO'] = df['TIPO_MODULO'].str.lower()
        if 'ATRIBUTO' in df.columns and not df['ATRIBUTO'].isna().all():
            df['ATRIBUTO'] = df['ATRIBUTO'].str.lower()
        df['ACAO'] = df['ACAO'].str.lower()

        df['ACAO'] = df['ACAO'].map(lambda x: calcular_similaridade(x, 1))
        df['TIPO_MODULO'] = df['TIPO_MODULO'].map(lambda x: calcular_similaridade(x, 2))
        if 'ATRIBUTO' in df.columns and not df['ATRIBUTO'].isna().all():
            df['ATRIBUTO'] = df['ATRIBUTO'].map(lambda x: x.replace('_', '').strip().lower())

        df = df.map(remover_acentos)

        return df

def limpar_dados(df, fun=None):
    """
    Limpa o DataFrame removendo linhas e colunas completamente vazias.

    Args:
        df (pd.DataFrame): DataFrame a ser limpo.

    Returns:
        pd.DataFrame: DataFrame sem linhas e colunas completamente vazias.
    """

    if fun is None:
        df = df.replace('nan', None)

        df = df.dropna(how='all')
        df = df.dropna(axis=1, how='all')
        return df
    else:
        df = df.replace('nan', None)
        df = df.dropna(how='all')
        colunas_protegidas = [col for col in df.columns if col in ['NOVO_VALOR', 'ATRIBUTO']]
        colunas_para_remover = [col for col in df.columns
                                if col not in colunas_protegidas and df[col].isna().all()]
        df = df.drop(columns=colunas_para_remover)

        return df

def format_panel(valor):
    if isinstance(valor, str):
        valor = valor.strip()
        valor = valor.replace(',', '.')  # Substituir vírgula decimal por ponto
        valor = re.sub(r'[^\d.-]', '', valor)  # Remover caracteres indesejados

        try:
            num = float(valor)  # Converter para número
            # Formatar com separador de milhares como ponto e decimal como vírgula
            return f"{num:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except ValueError:
            return None  # Se não for possível converter, retorna None

    return valor  # Se já for numérico, retorna diretamente

def normalize_number(value):
    if isinstance(value, str):
        value = value.strip()  # Remove espaços extras
        value = value.replace(',', '.')  # Troca vírgula decimal por ponto
        value = re.sub(r'[^\d.-]', '', value)  # Remove tudo que não for número, ponto ou traço (para negativos)

        if value.count('.') > 1:
            # Se houver mais de um ponto decimal, tentar corrigir
            parts = value.split('.')
            value = parts[0] + '.' + ''.join(parts[1:])  # Mantém o primeiro ponto decimal apenas

        try:
            num = float(value)  # Converte para float
            return int(num) if num.is_integer() else num  # Retorna int se for inteiro exato
        except ValueError:
            print(f"Erro ao converter valor: {value}")  # Depuração
            return None  # Se não for número válido, retorna None

    return value  # Se já for numérico, retorna diretamente
