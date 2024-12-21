import psycopg2
from psycopg2.extensions import connection
from contextlib import contextmanager

from .cfg import DB_PARAMS


class Database:
    def __init__(self):
        self.conn = None

    def get_connection(self):
        if self.conn is None:
            self.conn = psycopg2.connect(**DB_PARAMS)
            self.conn.autocommit = True
        return self.conn

    @contextmanager
    def get_cursor(self):
        try:
            cur = self.get_connection().cursor()
            yield cur
            self.conn.commit()
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            self.conn: connection = psycopg2.connect(**DB_PARAMS)
            self.conn.autocommit = True
            cur = self.conn.cursor()
            yield cur


db = Database()
