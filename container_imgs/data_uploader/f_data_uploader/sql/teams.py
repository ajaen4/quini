from f_data_uploader.database import db


def insert_teams(teams: list[tuple]):
    with db.get_cursor() as cur:
        query = """
            INSERT INTO bavariada.teams (id, name)
            VALUES (%s, %s)
            ON CONFLICT (id) DO NOTHING
        """

        cur.executemany(query, teams)


def get_team_id(team_id: str):
    with db.get_cursor() as cur:
        query = """
            SELECT id
            FROM bavariada.teams
            WHERE loterias_id = %s
        """

        cur.execute(query, (team_id,))

        team_id = cur.fetchone()

    return team_id[0]
