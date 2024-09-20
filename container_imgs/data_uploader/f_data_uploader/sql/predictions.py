from f_data_uploader.cfg import conn
from psycopg2 import sql


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
