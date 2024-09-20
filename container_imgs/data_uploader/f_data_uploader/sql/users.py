from f_data_uploader.cfg import conn


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
