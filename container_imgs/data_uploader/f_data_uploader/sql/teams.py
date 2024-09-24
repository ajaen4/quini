from f_data_uploader.cfg import conn
from psycopg2 import sql
from itertools import chain

from f_data_uploader.logger import logger


def has_one_spanish_match(team_names: list[str]) -> bool:
    cur = conn.cursor()
    cur.execute(
        sql.SQL(
            """
            SELECT name
            FROM bavariada.teams
            WHERE name IN %s
            AND HOME_CHAMPIONSHIP IN ('LA_LIGA', 'LA_LIGA_2');
            """
        ),
        (tuple(team_names),),
    )

    teams_in_db = list(chain(*cur.fetchall()))
    cur.close()

    if len(teams_in_db) == 0:
        teams_not_in_db = [
            team_name
            for team_name in team_names
            if team_name not in teams_in_db
        ]
        logger.info(f"No spanish league teams: {teams_not_in_db}")
        return False

    return True


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
