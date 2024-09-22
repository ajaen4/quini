from f_data_uploader.cfg import conn
from psycopg2 import sql
from itertools import chain

from f_data_uploader.logger import logger


def is_spanish_league(team_names: list[str]) -> bool:
    cur = conn.cursor()
    cur.execute(
        sql.SQL(
            """
            SELECT name
            FROM bavariada.teams
            WHERE name IN %s
            """
        ),
        (tuple(team_names),),
    )

    teams_in_db = list(chain(*cur.fetchall()))
    cur.close()

    if len(teams_in_db) != len(team_names):
        teams_not_in_db = [
            team_name
            for team_name in team_names
            if team_name not in teams_in_db
        ]
        logger.info(f"Teams not in db {teams_not_in_db}")
        return False

    return True
