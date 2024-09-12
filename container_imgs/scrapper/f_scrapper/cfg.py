import os
import json
import psycopg2
from psycopg2.extensions import connection
import boto3

from f_scrapper.aws.ssm import SSM


session = boto3.Session()
ssm_client = SSM(session)

secrets = json.loads(
    ssm_client.get_parameter("/quiniela/secrets", decrypt=True)
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
FOOTBALL_API = os.environ["FOOTBALL_API"]
RAPID_API_KEY = secrets["RAPID_API_KEY"]
