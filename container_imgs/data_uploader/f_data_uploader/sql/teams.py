from f_data_uploader.cfg import conn
from psycopg2 import sql


def insert_teams(teams: list[tuple]):
    cur = conn.cursor()

    query = sql.SQL(
        """
        INSERT INTO bavariada.teams (id, name)
        VALUES (%s, %s)
        ON CONFLICT (id) DO NOTHING
    """
    )

    cur.executemany(query, teams)
    conn.commit()

    cur.close()
