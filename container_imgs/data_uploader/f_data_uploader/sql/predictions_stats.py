from psycopg2 import sql
from psycopg2.extras import execute_values

from f_data_uploader.cfg import conn


def insert_predictions_stats(season_matchday: dict, predictions_stats: dict):
    cur = conn.cursor()

    query = sql.SQL(
        """
        INSERT INTO bavariada.predictions_stats (
            season,
            matchday,
            match_num,
            home_percent,
            draw_percent,
            away_percent
        )
        VALUES %s
        ON CONFLICT (season, matchday, match_num)
        DO UPDATE SET
            home_percent = EXCLUDED.home_percent,
            draw_percent = EXCLUDED.draw_percent,
            away_percent = EXCLUDED.away_percent
        """
    )
    values = [
        (
            season_matchday["season"],
            season_matchday["matchday"],
            match_num,
            prediction_stats["valor1"],
            prediction_stats["valorx"],
            prediction_stats["valor2"],
        )
        for match_num, prediction_stats in predictions_stats.items()
        if match_num != "14"
    ]

    execute_values(cur, query, values)
    conn.commit()

    cur.close()
