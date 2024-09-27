from psycopg2 import sql
from psycopg2.extras import execute_values

from f_data_uploader.cfg import conn
from f_data_uploader.logger import logger


def get_predictions(matchday: dict) -> list[str]:
    cur = conn.cursor()
    cur.execute(
        sql.SQL(
            """
            SELECT
                user_id,
                season,
                matchday,
                array_agg(
                    grouped_predictions
                    ORDER BY match_num
                ) AS match_predictions
            FROM (
                SELECT
                    user_id,
                    season,
                    matchday,
                    match_num,
                    array_agg(prediction ORDER BY col_num) AS grouped_predictions
                FROM
                    bavariada.predictions
                WHERE season = %s
                AND matchday = %s
                GROUP BY
                    user_id, season, matchday, match_num
            ) subquery
            GROUP BY
                user_id, season, matchday;
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
        INSERT INTO bavariada.predictions (user_id, season, matchday, col_num, match_num, prediction)
        VALUES %s
        ON CONFLICT (user_id, season, matchday, col_num, match_num)
        DO UPDATE SET
            prediction = EXCLUDED.prediction
        """
    )
    values = [
        (
            user_result["user_id"],
            user_result["season"],
            user_result["matchday"],
            user_result["col_num"],
            user_result["match_num"],
            user_result["prediction"],
        )
        for user_result in users_predictions
    ]

    execute_values(cur, query, values)
    conn.commit()

    uploaded_infos = {
        (
            user_predictions["user_id"],
            user_predictions["season"],
            user_predictions["matchday"],
        )
        for user_predictions in users_predictions
    }
    for uploaded_info in uploaded_infos:
        logger.info(
            f"Successfully upserted predictions for user {uploaded_info[0]}"
            f" in season {uploaded_info[1]} matchday {uploaded_info[2]}"
        )

    cur.close()
