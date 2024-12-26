from f_data_uploader.database import db
from f_data_uploader.logger import logger


def insert_matchday(matchday: dict, sorteo_id: int):
    cur = db.get_conn().cursor()
    cur.execute(
        """
        INSERT INTO bavariada.matchdays (season, matchday, status, start_datetime, sorteo_id)
        VALUES (%s, %s, 'NOT_STARTED', %s, %s)
        """,
        (
            matchday["temporada"],
            matchday["jornada"],
            matchday["start_datetime"],
            sorteo_id,
        ),
    )
    cur.close()


def matchday_exists(matchday: dict) -> bool:
    cur = db.get_conn().cursor()
    cur.execute(
        """
        SELECT matchday FROM bavariada.matchdays
        WHERE matchday = %s
        AND season = %s
        """,
        (
            matchday["jornada"],
            matchday["temporada"],
        ),
    )
    exists = cur.fetchone() is not None
    cur.close()

    return exists


def get_matchdays(status: str, limit: int = None) -> list[dict]:
    cur = db.get_conn().cursor()

    if limit:
        query = f"""
        SELECT * FROM bavariada.matchdays
        WHERE status = %s
        ORDER BY matchday desc
        LIMIT {limit}
        """
    else:
        query = """
        SELECT * FROM bavariada.matchdays
        WHERE status = %s
        """

    cur.execute(
        query,
        (status,),
    )

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    matchdays = [
        {columns[i]: value for i, value in enumerate(row)} for row in rows
    ]

    cur.close()

    return matchdays


def update_matchday_status(matchday: dict, status: str):
    cur = db.get_conn().cursor()
    cur.execute(
        """
        UPDATE bavariada.matchdays
        SET status = %s
        WHERE season = %s
        AND matchday = %s
        """,
        (
            status,
            matchday["season"],
            matchday["matchday"],
        ),
    )

    affected_rows = cur.rowcount
    cur.close()

    if affected_rows > 0:
        logger.info(
            f"Successfully updated matchday {matchday} status to FINISHED"
        )
    else:
        raise Exception(f"No matchday found with number {matchday}")
