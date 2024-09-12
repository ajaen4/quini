from psycopg2 import sql

from f_scrapper.cfg import conn
from f_scrapper.logger import logger


def upload_points(users_points: list[dict]):
    cur = conn.cursor()

    for user_points in users_points:
        cur.execute(
            sql.SQL(
                """
                INSERT INTO quiniela.points (user_id, matchday, points)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, matchday)
                DO UPDATE SET
                    points = EXCLUDED.points
                """
            ),
            (
                user_points["user_id"],
                user_points["matchday"],
                user_points["points"],
            ),
        )

        logger.info(
            f"Successfully upserted points for user {user_points['user_id']} in matchday {user_points['matchday']}"
        )

    conn.commit()

    cur.close()
