from f_data_uploader.cfg import conn
from psycopg2 import sql


def get_home_chmps(team_ids: list[str]) -> list[tuple]:
    cur = conn.cursor()
    cur.execute(
        sql.SQL(
            """
            SELECT home_championship
            FROM bavariada.teams
            WHERE id IN %s
            """
        ),
        (tuple(team_ids),),
    )

    home_chmps = [row[0] for row in cur.fetchall()]
    cur.close()

    return home_chmps
