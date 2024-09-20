from psycopg2 import sql
from psycopg2.extras import execute_values

from f_data_uploader.cfg import conn
from f_data_uploader.logger import logger


def insert_results(users_results: list[dict]):
    cur = conn.cursor()

    query = sql.SQL(
        """
        INSERT INTO bavariada.points (user_id, season, matchday, points, debt_euros)
        VALUES %s
        ON CONFLICT (user_id, season, matchday)
        DO UPDATE SET
            points = EXCLUDED.points,
            debt_euros = EXCLUDED.debt_euros
        """
    )
    values = [
        (
            user_result["user_id"],
            user_result["season"],
            user_result["matchday"],
            user_result["points"],
            user_result["debt_euros"],
        )
        for user_result in users_results
    ]

    execute_values(cur, query, values)
    conn.commit()

    for user_result in users_results:
        logger.info(
            f"Successfully upserted points for user {user_result['user_id']}"
            f" in season {user_result['season']} matchday {user_result['matchday']}"
        )

    cur.close()
