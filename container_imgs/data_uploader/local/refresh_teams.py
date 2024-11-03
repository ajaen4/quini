from csv import DictReader

from psycopg2 import sql
from psycopg2.extras import execute_values
from dotenv import load_dotenv

from f_data_uploader.cfg import conn

load_dotenv(".env")


def refresh_teams(file_path: str):
    with open(file_path, mode="r", encoding="utf-8") as file:
        csv_reader = DictReader(file, delimiter=";")
        teams_data = list(csv_reader)

    cur = conn.cursor()

    query = sql.SQL(
        """
        INSERT INTO bavariada.teams (
            id,
            name,
            league_id,
            loterias_id,
            code,
            logo_url
        )
        VALUES %s
        ON CONFLICT (id)
        DO UPDATE SET
            loterias_id = EXCLUDED.loterias_id,
            code = EXCLUDED.code,
            logo_url = EXCLUDED.logo_url,
            league_id = EXCLUDED.league_id
        """
    )

    values = [
        (
            team_data["id"],
            team_data["name"],
            team_data["league_id"],
            team_data["loterias_id"],
            team_data["code"],
            team_data["logo_url"],
        )
        for team_data in teams_data
    ]

    execute_values(cur, query, values)
    conn.commit()

    cur.close()


if __name__ == "__main__":
    refresh_teams("teams_rows.csv")
