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


def get_team_id(team_id: str):
    cur = conn.cursor()

    query = sql.SQL(
        """
        SELECT id
        FROM bavariada.teams
        WHERE loterias_id = %s
        """
    )

    cur.execute(query, (team_id,))
    conn.commit()

    team_id = cur.fetchone()

    cur.close()

    return team_id[0]
