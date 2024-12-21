import psycopg2
from psycopg2.extensions import connection

from .cfg import DB_PARAMS


class Database:
    def __init__(self):
        self.conn: connection = None

    def get_conn(self):
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(**DB_PARAMS)
            self.conn.autocommit = True
        return self.conn


db = Database()
