from psycopg2 import sql

from f_data_uploader.cfg import conn
from f_data_uploader.logger import logger


def update_matchday_status(match_results: list[dict]):
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
        INSERT INTO bavariada.matchdays (season, matchday, status)
        VALUES (%s, %s, 'NOT_STARTED')
        """
        ),
        (matchday["temporada"], matchday["jornada"]),
    )
    conn.commit()

    cur.close()


def insert_matches(matches: dict):
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TEMPORARY TABLE temp_matches (
            season VARCHAR(9),
            matchday INTEGER,
            match_num INTEGER,
            home_name VARCHAR(50),
            away_name VARCHAR(50)
        );
        """
    )
    conn.commit()

    matches_team_names = list()
    for match_num, match in enumerate(matches["partidos"]):
        matches_team_names.append(
            (
                matches["temporada"],
                matches["jornada"],
                match_num,
                match["local"],
                match["visitante"],
            )
        )

    cur.executemany(
        sql.SQL(
            """
            INSERT INTO temp_matches (season, matchday, match_num, home_name, away_name)
            VALUES (%s, %s, %s, %s, %s);
            """
        ),
        matches_team_names,
    )
    conn.commit()

    cur.execute(
        sql.SQL(
            """
            INSERT INTO bavariada.matches (season, matchday, match_num, home_team_id, away_team_id)
            SELECT
                tm.season,
                tm.matchday,
                tm.match_num,
                home_team.id AS home_team_id,
                away_team.id AS away_team_id
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
