from psycopg2 import sql

from f_scrapper.cfg import conn
from f_scrapper.logger import logger


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
        (matchday,)
    )

    affected_rows = cur.rowcount
    conn.commit()

    cur.close()

    if affected_rows > 0:
        logger.info(f"Successfully updated matchday {matchday} status to FINISHED")
    else:
        raise Exception(f"No matchday found with number {matchday}")


def upload_matches(matches: list, matchday: int):
    cur = conn.cursor()

    cur.execute(
        sql.SQL(
            """
            INSERT INTO bavariada.matchdays (matchday)
            VALUES (%s)
            """
        ),
        (matchday,),
    )

    for match in matches:
        cur.execute(
            sql.SQL(
                """
            INSERT INTO bavariada.matches (id, league_id, matchday, match_num, home_team_id, away_team_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            ),
            (
                match["id"],
                match["league_id"],
                matchday,
                match["match_num"],
                match["home_team_id"],
                match["away_team_id"],
            ),
        )

    conn.commit()
    logger.info(
        f"Successfully uploaded {len(matches)} matches for Jornada {matchday}"
    )

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
