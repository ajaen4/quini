from psycopg2 import sql
from psycopg2.extras import execute_values

from f_data_uploader.cfg import conn
from f_data_uploader.logger import logger


def get_predictions(matchday: dict) -> list[str]:
    cur = conn.cursor()
    cur.execute(
        sql.SQL(
            """
            SELECT *
            FROM bavariada.predictions
            WHERE season = %s
            AND matchday = %s
            """
        ),
        (
            matchday["season"],
            matchday["matchday"],
        ),
    )

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    predictions = [
        {columns[i]: value for i, value in enumerate(row)} for row in rows
    ]

    cur.close()

    return predictions


def insert_predictions(users_predictions: list[dict]):
    cur = conn.cursor()

    query = sql.SQL(
        """
        INSERT INTO bavariada.predictions (user_id, season, matchday, match_num, predictions)
        VALUES %s
        ON CONFLICT (user_id, season, matchday, match_num)
        DO UPDATE SET
            predictions = EXCLUDED.predictions
        """
    )
    values = [
        (
            user_result["user_id"],
            user_result["season"],
            user_result["matchday"],
            user_result["match_num"],
            user_result["prediction"],
        )
        for user_result in users_predictions
    ]

    execute_values(cur, query, values)
    conn.commit()

    for user_result in users_predictions:
        logger.info(
            f"Successfully upserted predictions for user {user_result['user_id']}"
            f" in season {user_result['season']} matchday {user_result['matchday']}"
        )

    cur.close()
