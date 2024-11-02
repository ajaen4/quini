import requests
from csv import DictWriter
import json

import boto3

from f_data_uploader.aws.ssm import SSM


def download_teams(season: int, league_ids: list[int]):

    ssm_client = SSM(boto3.Session(region_name="eu-west-1"))

    headers = json.loads(
        ssm_client.get_parameter("/api-football/headers", decrypt=True)
    )

    teams_data = list()
    for league_id in league_ids:
        params = {"season": season, "league": league_id}
        response = requests.get(
            "https://v3.football.api-sports.io/teams",
            headers=headers,
            params=params,
        )
        response.raise_for_status()

        teams = response.json()["response"]
        for team in teams:
            if team["team"]["id"] == 5254:
                team["team"]["code"] = "CAS"
            if team["team"]["id"] == 9692:
                team["team"]["code"] = "ELD"

            team_data = {
                "api_id": team["team"]["id"],
                "code": team["team"]["code"],
                "logo_url": team["team"]["logo"],
                "league_id": league_id,
            }

            teams_data.append(team_data)

    with open(f"teams_{season}.csv", "w", newline="") as file:
        writer = DictWriter(
            file, fieldnames=["api_id", "code", "league_id", "logo_url"]
        )
        writer.writeheader()
        writer.writerows(teams_data)


if __name__ == "__main__":
    download_teams(2024, [140, 141])
