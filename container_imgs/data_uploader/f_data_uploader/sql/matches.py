from datetime import datetime

from psycopg2 import sql

from f_data_uploader.cfg import conn
from f_data_uploader.logger import logger
from f_data_uploader.strings import team_name_to_id


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

    cur.execute(
        """
        CREATE TEMPORARY TABLE temp_matches (
            season VARCHAR(9),
            matchday INTEGER,
            match_num INTEGER,
            home_name VARCHAR(50),
            away_name VARCHAR(50),
            kickoff_datetime TIMESTAMP
        );
        """
    )
    conn.commit()

    matches_team_names = list()
    for match_num, match in enumerate(matchday["partidos"]):

        match_date = datetime.strptime(
            match["fecha"], "%Y/%m/%d %H:%M:%S"
        ).strftime("%Y-%m-%d %H:%M:%S")
        matches_team_names.append(
            (
                matchday["temporada"],
                matchday["jornada"],
                match_num,
                match["local"],
                match["visitante"],
                match_date,
            )
        )

    cur.executemany(
        sql.SQL(
            """
            INSERT INTO temp_matches (season, matchday, match_num, home_name, away_name, kickoff_datetime)
            VALUES (%s, %s, %s, %s, %s, %s);
            """
        ),
        matches_team_names,
    )
    conn.commit()

    cur.execute(
        sql.SQL(
            """
            INSERT INTO bavariada.matches (season, matchday, match_num, home_team_id, away_team_id, kickoff_datetime)
            SELECT
                tm.season,
                tm.matchday,
                tm.match_num,
                home_team.id AS home_team_id,
                away_team.id AS away_team_id,
                tm.kickoff_datetime
            FROM temp_matches tm
            JOIN bavariada.teams home_team ON tm.home_name = home_team.name
            JOIN bavariada.teams away_team ON tm.away_name = away_team.name
            """
        )
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
        team_ids.add(team_name_to_id(match["local"]))
        team_ids.add(team_name_to_id(match["visitante"]))

    cur.execute(
        """
        SELECT id, home_championship
        FROM bavariada.teams
        WHERE id = ANY(%s)
        """,
        (list(team_ids),),
    )
    team_championships = {str(row[0]): row[1] for row in cur.fetchall()}

    for match in matches:
        local_championship = team_championships.get(
            team_name_to_id(match["local"])
        )
        away_championship = team_championships.get(
            team_name_to_id(match["visitante"])
        )

        if local_championship == "LA_LIGA" and away_championship == "LA_LIGA":
            logger.info("Found at least one la liga match")
            return True

    logger.info("Didn't find any la liga match, skipping matchday upload")
    return False
