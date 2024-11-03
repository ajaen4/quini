import os
import json
import psycopg2
from psycopg2.extensions import connection
import boto3

from f_data_uploader.aws.ssm import SSM


session = boto3.Session()
ssm_client = SSM(session)

secrets = json.loads(
    ssm_client.get_parameter("/bavariada/secrets", decrypt=True)
)

DB_HOST = secrets["DB_HOST"]
DB_PORT = secrets["DB_PORT"]
DB_NAME = secrets["DB_NAME"]
DB_USERNAME = secrets["DB_USERNAME"]
DB_PASSWORD = secrets["DB_PASSWORD"]

DB_PARAMS = {
    "dbname": DB_NAME,
    "user": DB_USERNAME,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": DB_PORT,
}
conn: connection = psycopg2.connect(**DB_PARAMS)

QUINIELA_URL = os.environ["QUINIELA_URL"]
LOTERO_URL = os.environ["LOTERO_URL"]
LOTERO_TOKEN = secrets["LOTERO_TOKEN"]
FOOT_API_URL = os.environ["FOOT_API_URL"]
FOOT_API_TOKEN = secrets["FOOT_API_TOKEN"]
