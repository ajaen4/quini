from psycopg2.extras import execute_values, execute_batch

from f_data_uploader.database import db
from f_data_uploader.logger import logger


def get_matchday_points(matchday: dict) -> list[str]:
    with db.get_cursor() as cur:
        cur.execute(
            """
            WITH col_points as (
                select user_id, season, matchday, col_num, count(*) as points
                from bavariada.predictions
                where season = %s and matchday = %s and is_correct = true
                group by user_id, season, matchday, col_num
            )

            SELECT user_id, season, matchday, max(points) as points
            FROM col_points
            GROUP BY user_id, season, matchday;
            """,
            (
                matchday["season"],
                matchday["matchday"],
            ),
        )

        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()

        matchday_points = [
            {columns[i]: value for i, value in enumerate(row)} for row in rows
        ]

    return matchday_points


def insert_predictions(users_predictions: list[dict]):
    with db.get_cursor() as cur:
        query = """
            INSERT INTO bavariada.predictions (user_id, season, matchday, col_num, match_num, prediction, is_elige8)
            VALUES %s
            ON CONFLICT (user_id, season, matchday, col_num, match_num)
            DO UPDATE SET
                prediction = EXCLUDED.prediction,
                is_elige8 = EXCLUDED.is_elige8
        """
        values = [
            (
                user_predictions["user_id"],
                user_predictions["season"],
                user_predictions["matchday"],
                user_predictions["col_num"],
                user_predictions["match_num"],
                user_predictions["prediction"],
                user_predictions["is_elige8"],
            )
            for user_predictions in users_predictions
        ]

        execute_values(cur, query, values)

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


def update_predictions(matches: list[dict]):
    with db.get_cursor() as cur:
        query = """
            UPDATE bavariada.predictions
            SET is_correct = (prediction = %s)
            WHERE season = %s AND matchday = %s AND match_num = %s
        """
        values = [
            (
                match["result"],
                match["season"],
                match["matchday"],
                match["match_num"],
            )
            for match in matches
        ]

        execute_batch(cur, query, values)
