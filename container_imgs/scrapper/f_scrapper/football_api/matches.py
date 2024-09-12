import requests

from datetime import datetime, timedelta

import f_scrapper.cfg as cfg

headers = {
    "X-RapidAPI-Host": cfg.FOOTBALL_API,
    "X-RapidAPI-Key": cfg.RAPID_API_KEY,
}


def map_matches(matches: list[dict], league_id: int) -> list[dict]:
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    current_date = datetime.now()
    one_week_later = current_date + timedelta(days=10)
    querystring = {
        "league": league_id,
        "season": current_date.year,
        "from": current_date.strftime("%Y-%m-%d"),
        "to": one_week_later.strftime("%Y-%m-%d"),
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code != 200:
        raise Exception(
            f"Error: Unable to fetch data for league {league_id}. Status code: {response.status_code}"
        )

    all_matches = response.json()["response"]

    fixture_map = {
        (match["teams"]["home"]["id"], match["teams"]["away"]["id"]): {
            "league_id": match["league"]["id"],
            "fixture_id": match["fixture"]["id"],
        }
        for match in all_matches
        if match["league"]["id"] == league_id
    }

    for match in matches:
        key = (match["home_team_id"], match["away_team_id"])
        if key in fixture_map:
            match["league_id"] = fixture_map[key]["league_id"]
            match["id"] = fixture_map[key]["fixture_id"]

    return matches


def get_results(match_ids: list[int]) -> dict[int, dict]:
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    results = dict()
    querystring = {
        "ids": "-".join([str(match_id) for match_id in match_ids]),
        "status": "FT",
    }

    response = requests.get(url, headers=headers, params=querystring)

    for match in response.json()["response"]:
        match_id = match["fixture"]["id"]
        if response.status_code != 200:
            raise Exception(
                f"Error: Unable to fetch data for match_id {match_id}. Status code: {response.status_code}"
            )

        results[match_id] = match["score"]["fulltime"]

    return results
