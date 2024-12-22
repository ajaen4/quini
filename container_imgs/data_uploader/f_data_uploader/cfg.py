import os
import json
import boto3

from f_data_uploader.aws.ssm import SSM

ENV = os.environ["ENV"]

session = boto3.Session()
ssm_client = SSM(session)

secrets = json.loads(
    ssm_client.get_parameter(f"/quini/secrets/{ENV}", decrypt=True)
)

DB_HOST = secrets["DB_HOST"]
SERVERLESS_DB_PORT = secrets["SERVERLESS_DB_PORT"]
DB_NAME = secrets["DB_NAME"]
DB_USERNAME = secrets["DB_USERNAME"]
DB_PASSWORD = secrets["DB_PASSWORD"]

DB_PARAMS = {
    "dbname": DB_NAME,
    "user": DB_USERNAME,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": SERVERLESS_DB_PORT,
}

LOTERIAS_URL = os.environ["LOTERIAS_URL"]
LOTERO_URL = os.environ["LOTERO_URL"]
LOTERO_TOKEN = secrets["LOTERO_TOKEN"]
FOOT_API_URL = os.environ["FOOT_API_URL"]
FOOT_API_TOKEN = secrets["FOOT_API_TOKEN"]

LOTERO_HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "es-ES,es;q=0.9,en;q=0.8",
    "content-type": "application/json",
    "dnt": "1",
    "origin": "https://juegos.loteriasyapuestas.es",
    "referer": "https://juegos.loteriasyapuestas.es/",
    "sec-ch-ua": '"Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}
