from f_scrapper.cfg import conn


def get_teams_mapping() -> list[dict]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM bavariada.teams")

    columns = [desc[0] for desc in cur.description]

    rows = cur.fetchall()

    team_mappings = [
        {columns[i]: value for i, value in enumerate(row)} for row in rows
    ]

    cur.close()

    return team_mappings
