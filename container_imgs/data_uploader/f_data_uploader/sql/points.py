from psycopg2 import sql

from f_data_uploader.cfg import conn
from f_data_uploader.logger import logger


def upload_points(users_points: list[dict]):
    cur = conn.cursor()

    for user_points in users_points:
        cur.execute(
            sql.SQL(
                """
                INSERT INTO bavariada.points (user_id, season, matchday, points)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, season, matchday)
                DO UPDATE SET
                    points = EXCLUDED.points
                """
            ),
            (
                user_points["user_id"],
                user_points["season"],
                user_points["matchday"],
                user_points["points"],
            ),
        )

        logger.info(
            f"Successfully upserted points for user {user_points['user_id']}"
            f" in season {user_points['season']} matchday {user_points['matchday']}"
        )

    conn.commit()

    cur.close()
