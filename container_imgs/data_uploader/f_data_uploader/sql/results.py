from psycopg2.extras import execute_values

from f_data_uploader.cfg import conn
from f_data_uploader.logger import logger


def insert_results(users_results: list[dict]):
    cur = conn.cursor()

    query = """
        INSERT INTO bavariada.results (user_id, season, matchday, points, debt_euros)
        VALUES %s
        ON CONFLICT (user_id, season, matchday)
        DO UPDATE SET
            points = EXCLUDED.points,
            debt_euros = EXCLUDED.debt_euros
    """
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


def insert_prices(users_prices: list[dict]):
    cur = conn.cursor()

    query = """
        UPDATE bavariada.results
        SET price_euros = data.price_euros
        FROM (VALUES %s) AS data(user_id, season, matchday, price_euros)
        WHERE bavariada.results.user_id = data.user_id::uuid
          AND bavariada.results.season = data.season
          AND bavariada.results.matchday = data.matchday::integer
    """

    values = [
        (
            user_prices["user_id"],
            user_prices["season"],
            user_prices["matchday"],
            user_prices["price_euros"],
        )
        for user_prices in users_prices
    ]

    execute_values(cur, query, values)

    conn.commit()

    for user_price in users_prices:
        logger.info(
            f"Successfully updated price for user {user_price['user_id']}"
            f" in season {user_price['season']} matchday {user_price['matchday']}"
        )

    cur.close()
