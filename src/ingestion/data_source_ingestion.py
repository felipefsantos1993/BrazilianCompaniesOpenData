import os
import re
import zipfile
import requests
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth
from pyspark.sql import SparkSession
from pyspark.sql.functions import max as spark_max

# =========================
# SPARK SESSION
# =========================
spark = SparkSession.getActiveSession()

# =========================
# CONFIG
# =========================
BASE_URL = "https://arquivos.receitafederal.gov.br/public.php/webdav/Dados/Cadastros/CNPJ/"
TOKEN = "gn672Ad4CF8N6TK"

DESTINO_BASE = "/Volumes/..."

DESTINO_ZIPS = os.path.join(DESTINO_BASE, "ZIPS")
DESTINO_EMPRESAS = os.path.join(DESTINO_BASE, "EMPRESAS")
DESTINO_ESTAB = os.path.join(DESTINO_BASE, "ESTABELECIMENTOS")

HEADERS = {"OCS-APIRequest": "true"}
NAMESPACE = {"d": "DAV:"}

TABLE_NAME = "development.landing_raw.ldz_raw_receita_federal_empresas"

# =========================
# UTIL
# =========================
def log(msg):
    print(f"[INFO] {msg}")


def table_exists(table_name):
    return spark.catalog.tableExists(table_name)


# =========================
# VALIDAÇÃO DA CARGA
# =========================
def should_process(latest_folder):
    """
    Realiza a carga somente quando:
        max(ano_mes_origem) > max(ano_mes_tabela)
    """

    if not re.fullmatch(r"\d{4}-\d{2}", latest_folder):
        raise Exception(f"Formato inválido da competência: {latest_folder}")

    origem_ano_mes = int(latest_folder.replace("-", ""))

    log(f"Maior competência da origem : {origem_ano_mes}")

    # Primeira carga
    if not table_exists(TABLE_NAME):
        log("Tabela não encontrada. Primeira carga.")
        return True

    df = spark.table(TABLE_NAME)

    # Tabela vazia
    if df.limit(1).count() == 0:
        log("Tabela vazia. Primeira carga.")
        return True

    if "ano_mes" not in df.columns:
        raise Exception(f"A coluna ano_mes não existe na tabela {TABLE_NAME}")

    tabela_ano_mes = (
        df.select(spark_max("ano_mes").alias("ano_mes"))
          .collect()[0]["ano_mes"]
    )

    if tabela_ano_mes is None:
        log("Tabela sem registros.")
        return True

    tabela_ano_mes = int(tabela_ano_mes)

    log(f"Maior competência da tabela : {tabela_ano_mes}")

    if origem_ano_mes > tabela_ano_mes:
        log("Nova competência encontrada. Iniciando coleta.")
        return True

    log("A tabela já possui a competência mais recente. Processo finalizado.")
    return False


# =========================
# RECEITA FEDERAL
# =========================
def get_latest_folder():

    response = requests.request(
        "PROPFIND",
        BASE_URL,
        headers=HEADERS,
        auth=HTTPBasicAuth(TOKEN, ""),
        data="""<?xml version="1.0"?>
        <d:propfind xmlns:d="DAV:">
            <d:prop>
                <d:displayname/>
            </d:prop>
        </d:propfind>
        """
    )

    response.raise_for_status()

    root = ET.fromstring(response.content)

    folders = []

    for resp in root.findall("d:response", NAMESPACE):

        href = resp.find("d:href", NAMESPACE).text
        folder = href.rstrip("/").split("/")[-1]

        if re.fullmatch(r"\d{4}-\d{2}", folder):
            folders.append(folder)

    folders.sort()

    if not folders:
        return None

    return folders[-1]


def list_zip_files(folder):

    url = f"{BASE_URL}{folder}/"

    response = requests.request(
        "PROPFIND",
        url,
        headers=HEADERS,
        auth=HTTPBasicAuth(TOKEN, "")
    )

    response.raise_for_status()

    root = ET.fromstring(response.content)

    arquivos = []

    for resp in root.findall("d:response", NAMESPACE):

        href = resp.find("d:href", NAMESPACE).text

        if href.endswith(".zip"):
            arquivos.append(href.split("/")[-1])

    arquivos.sort()

    return arquivos


# =========================
# DOWNLOAD
# =========================
def download_files(folder, zip_files):

    os.makedirs(DESTINO_ZIPS, exist_ok=True)

    url = f"{BASE_URL}{folder}/"

    for file_name in zip_files:

        destino = os.path.join(DESTINO_ZIPS, file_name)

        if os.path.exists(destino):
            log(f"ZIP já existe: {file_name}")
            continue

        log(f"Baixando {file_name}")

        with requests.get(
            url + file_name,
            auth=HTTPBasicAuth(TOKEN, ""),
            stream=True
        ) as r:

            r.raise_for_status()

            with open(destino, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        log(f"Download concluído: {file_name}")


# =========================
# EXTRAÇÃO
# =========================
def extract_files(filter_name, replace_pattern, destino, latest_folder):

    ano_mes = latest_folder.replace("-", "")

    os.makedirs(destino, exist_ok=True)

    zip_files = [
        f
        for f in os.listdir(DESTINO_ZIPS)
        if filter_name in f and f.endswith(".zip")
    ]

    for zip_name in zip_files:

        zip_path = os.path.join(DESTINO_ZIPS, zip_name)

        log(f"Extraindo {zip_name}")

        try:

            with zipfile.ZipFile(zip_path, "r") as z:

                for member in z.namelist():

                    nome = member.replace(replace_pattern, "csv")

                    nome_base, extensao = os.path.splitext(nome)

                    novo_nome = f"{nome_base}_{ano_mes}{extensao}"

                    destino_arquivo = os.path.join(
                        destino,
                        novo_nome
                    )

                    if os.path.exists(destino_arquivo):
                        log(f"Arquivo já existe: {novo_nome}")
                        continue

                    with z.open(member) as source, open(destino_arquivo, "wb") as target:

                        while True:

                            chunk = source.read(8192)

                            if not chunk:
                                break

                            target.write(chunk)

                    log(f"Extraído: {novo_nome}")

        except Exception as e:
            log(f"Erro ao extrair {zip_name}: {e}")


# =========================
# MAIN
# =========================
def main():

    log("Iniciando processo Receita Federal")

    latest_folder = get_latest_folder()

    if latest_folder is None:
        log("Nenhuma competência encontrada.")
        return

    log(f"Maior competência encontrada na origem: {latest_folder}")

    if not should_process(latest_folder):
        return

    zip_files = list_zip_files(latest_folder)

    if not zip_files:
        log("Nenhum arquivo ZIP encontrado.")
        return

    download_files(latest_folder, zip_files)

    extract_files(
        "Empresas",
        "EMPRECSV",
        DESTINO_EMPRESAS,
        latest_folder
    )

    extract_files(
        "Estabelecimentos",
        "ESTABELE",
        DESTINO_ESTAB,
        latest_folder
    )

    log("Processo concluído com sucesso.")


if __name__ == "__main__":
    main()