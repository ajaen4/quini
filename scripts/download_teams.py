import re
import csv

import unidecode
import requests
from datetime import datetime

rapidapi_host = "api-football-v1.p.rapidapi.com"
rapidapi_key = "61a80f6c51msh8f57ee1e788e646p12608ajsn504e05a1388b"


def get_teams(league_id, season) -> list[dict]:
    url = "https://api-football-v1.p.rapidapi.com/v3/teams"

    querystring = {"league": league_id, "season": season}

    headers = {
        "X-RapidAPI-Host": rapidapi_host,
        "X-RapidAPI-Key": rapidapi_key,
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code != 200:
        raise Exception(
            f"Error: Unable to fetch data for league {league_id}. Status code: {response.status_code}"
        )

    all_teams = response.json()["response"]
    return [
        {
            "id": team_data["team"]["id"],
            "league_id": league_id,
            "name": clean_text(team_data["team"]["name"]),
        }
        for team_data in all_teams
    ]


def clean_text(text: str) -> str:
    text = unidecode.unidecode(text)

    cleaned_text = re.sub(r"[^a-zA-Z\s]", "", text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    return cleaned_text


def main():
    current_year = datetime.now().year

    la_liga_id = 140
    segunda_division_id = 141

    la_liga_teams = get_teams(la_liga_id, current_year)
    segunda_division_teams = get_teams(segunda_division_id, current_year)

    all_teams = la_liga_teams + segunda_division_teams

    csv_filename = f"spanish_teams_{current_year}.csv"

    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["id", "league_id", "name"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for team in all_teams:
            writer.writerow(team)

    print(f"Teams data for {current_year} has been saved to {csv_filename}")


if __name__ == "__main__":
    main()
