from f_data_uploader.cfg import conn

from psycopg2 import sql


def get_users() -> list[str]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, raw_user_meta_data->>'display_name' as display_name
        FROM auth.users
        """
    )

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    users = [
        {columns[i]: value for i, value in enumerate(row)} for row in rows
    ]

    cur.close()

    return users


def get_users_id(lotero_user_id: str) -> str:
    cur = conn.cursor()
    cur.execute(
        sql.SQL(
            """
            SELECT id
            FROM auth.users
            WHERE raw_user_meta_data->>'lotero_user_id' = %s
            """
        ),
        (lotero_user_id,),
    )

    rows = cur.fetchall()
    cur.close()

    return rows[0][0]
