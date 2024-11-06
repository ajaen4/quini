from datetime import datetime

from psycopg2 import sql

from f_data_uploader.cfg import conn
from f_data_uploader.logger import logger
from f_data_uploader.strings import get_loterias_id


def insert_matches(matchday: dict):
    cur = conn.cursor()

    values = list()
    for match_num, match in enumerate(matchday["partidos"]):
        match_date = datetime.strptime(
            match["fecha"], "%Y/%m/%d %H:%M:%S"
        ).strftime("%Y-%m-%d %H:%M:%S")

        values.append(
            (
                match["id"],
                matchday["temporada"],
                int(matchday["jornada"]),
                match_num,
                match["home_id"],
                match["away_id"],
                match_date,
            )
        )

    cur.executemany(
        sql.SQL(
            """
            INSERT INTO bavariada.matches (id, season, matchday, match_num, home_team_id, away_team_id, kickoff_datetime)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
        ),
        values,
    )
    conn.commit()

    cur.close()


def get_matches(matchday: int) -> list[dict]:
    cur = conn.cursor()
    cur.execute(
        sql.SQL(
            """
            SELECT *
            FROM bavariada.matches m
            WHERE m.matchday = %s
            ORDER BY m.match_num
            """
        ),
        (matchday,),
    )

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    matches = [
        {columns[i]: value for i, value in enumerate(row)} for row in rows
    ]

    cur.close()

    return matches


def has_one_spanish_match(matches: list[dict]) -> bool:
    cur = conn.cursor()
    team_ids = set()
    for match in matches:
        team_ids.add(get_loterias_id(match["local"]))
        team_ids.add(get_loterias_id(match["visitante"]))

    cur.execute(
        """
        SELECT loterias_id, league_id
        FROM bavariada.teams
        WHERE loterias_id = ANY(%s)
        """,
        (list(team_ids),),
    )
    team_championships = {str(row[0]): row[1] for row in cur.fetchall()}

    LA_LIGA_ID = 140
    for match in matches:
        local_league_id = team_championships.get(
            get_loterias_id(match["local"])
        )
        away_league_id = team_championships.get(
            get_loterias_id(match["visitante"])
        )

        if local_league_id == LA_LIGA_ID and away_league_id == LA_LIGA_ID:
            logger.info("Found at least one la liga match")
            return True

    logger.info("Didn't find any la liga match, skipping matchday upload")
    return False
