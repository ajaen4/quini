from datetime import datetime

from psycopg2 import sql

from f_data_uploader.cfg import conn
from f_data_uploader.logger import logger
from f_data_uploader.strings import team_name_to_loterias_id


def update_matchday_status(matchday: dict, status: str):
    cur = conn.cursor()

    cur.execute(
        sql.SQL(
            """
            UPDATE bavariada.matchdays
            SET status = %s
            WHERE season = %s
            AND matchday = %s
            """
        ),
        (
            status,
            matchday["season"],
            matchday["matchday"],
        ),
    )

    affected_rows = cur.rowcount
    conn.commit()

    cur.close()

    if affected_rows > 0:
        logger.info(
            f"Successfully updated matchday {matchday} status to FINISHED"
        )
    else:
        raise Exception(f"No matchday found with number {matchday}")


def insert_matchday(matchday: dict):
    cur = conn.cursor()

    cur.execute(
        sql.SQL(
            """
        INSERT INTO bavariada.matchdays (season, matchday, status, start_datetime)
        VALUES (%s, %s, 'NOT_STARTED', %s)
        """
        ),
        (
            matchday["temporada"],
            matchday["jornada"],
            matchday["start_datetime"],
        ),
    )
    conn.commit()

    cur.close()


def insert_matches(matchday: dict):
    cur = conn.cursor()

    values = list()
    for match_num, match in enumerate(matchday["partidos"]):
        match_date = datetime.strptime(
            match["fecha"], "%Y/%m/%d %H:%M:%S"
        ).strftime("%Y-%m-%d %H:%M:%S")

        values.append(
            (
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
            INSERT INTO bavariada.matches (season, matchday, match_num, home_team_id, away_team_id, kickoff_datetime)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        ),
        values,
    )
    conn.commit()

    cur.close()


def matchday_exists(matchday: dict) -> bool:
    cur = conn.cursor()
    cur.execute(
        sql.SQL(
            """
            SELECT matchday FROM bavariada.matchdays
            WHERE matchday = %s
            AND season = %s
            """,
        ),
        (
            matchday["jornada"],
            matchday["temporada"],
        ),
    )
    exists = cur.fetchone() is not None
    cur.close()
    return exists


def get_matchdays(status: str) -> list[dict]:
    cur = conn.cursor()
    cur.execute(
        sql.SQL("SELECT * FROM bavariada.matchdays WHERE status = %s"),
        (status,),
    )

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    matchdays = [
        {columns[i]: value for i, value in enumerate(row)} for row in rows
    ]

    cur.close()

    return matchdays


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
        team_ids.add(team_name_to_loterias_id(match["local"]))
        team_ids.add(team_name_to_loterias_id(match["visitante"]))

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
            team_name_to_loterias_id(match["local"])
        )
        away_league_id = team_championships.get(
            team_name_to_loterias_id(match["visitante"])
        )

        if local_league_id == LA_LIGA_ID and away_league_id == LA_LIGA_ID:
            logger.info("Found at least one la liga match")
            return True

    logger.info("Didn't find any la liga match, skipping matchday upload")
    return False
