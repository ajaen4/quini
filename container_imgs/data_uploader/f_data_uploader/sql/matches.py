from psycopg2 import sql

from f_data_uploader.cfg import conn
from f_data_uploader.logger import logger


def mark_matchday_finished(matchday: int):
    cur = conn.cursor()

    cur.execute(
        sql.SQL(
            """
            UPDATE bavariada.matchdays
            SET status = 'FINISHED'
            WHERE matchday = %s
            """
        ),
        (matchday,),
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


def insert_matchdays(matchdays: list[tuple]):
    cur = conn.cursor()

    query = sql.SQL(
        """
        INSERT INTO bavariada.matchdays (season, matchday, status)
        VALUES (%s, %s, %s)
        ON CONFLICT (season, matchday)  DO UPDATE SET
            status = EXCLUDED.status
    """
    )

    cur.executemany(query, matchdays)
    conn.commit()

    cur.close()


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


def insert_matches(matches: list[tuple]):
    cur = conn.cursor()

    query = sql.SQL(
        """
        INSERT INTO bavariada.matches (season, matchday, match_num, home_team_id, away_team_id)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (season, matchday, match_num) DO NOTHING
    """
    )

    cur.executemany(query, matches)
    conn.commit()

    cur.close()


def matchday_exists(matchday: str) -> bool:
    cur = conn.cursor()
    cur.execute(
        "SELECT matchday FROM bavariada.matchdays WHERE matchday = %s",
        (matchday,),
    )
    exists = cur.fetchone() is not None
    cur.close()
    return exists


def get_matchdays_in_progress() -> list[int]:
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM bavariada.matchdays WHERE status = 'IN_PROGRESS'"
    )

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    matchdays = [
        {columns[i]: value for i, value in enumerate(row)} for row in rows
    ]

    cur.close()

    return [matchday["matchday"] for matchday in matchdays]


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
