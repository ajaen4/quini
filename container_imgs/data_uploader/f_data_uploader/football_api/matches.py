import requests
import copy

import f_data_uploader.cfg as cfg
from f_data_uploader.sql import get_team_id
from f_data_uploader.strings import get_loterias_id


def add_match_ids(matchday: dict) -> dict:
    matchday_copy = copy.deepcopy(matchday)

    headers = {"x-rapidapi-key": cfg.FOOT_API_TOKEN}
    for match in matchday_copy["partidos"]:
        home_id = get_team_id(get_loterias_id(match["local"]))
        away_id = get_team_id(get_loterias_id(match["visitante"]))

        url = f"{cfg.FOOT_API_URL}/fixtures/headtohead"
        params = {
            "h2h": f"{home_id}-{away_id}",
            "next": 1,
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        match_info = response.json()["response"][0]["fixture"]

        match["id"] = match_info["id"]
        match["home_id"] = home_id
        match["away_id"] = away_id

    return matchday_copy


def get_matches_status(matches: list[str]):
    match_ids_param = "-".join([str(match["id"]) for match in matches])
    params = {"ids": match_ids_param}
    headers = {"x-rapidapi-key": cfg.FOOT_API_TOKEN}
    response = requests.get(
        f"{cfg.FOOT_API_URL}/fixtures",
        params=params,
        headers=headers,
    )
    response.raise_for_status()
    data = response.json()
    fixtures_status = [
        {
            "id": fixture["fixture"]["id"],
            "status": fixture["fixture"]["status"]["short"],
            "home_goals": fixture["goals"]["home"],
            "away_goals": fixture["goals"]["away"],
        }
        for fixture in data["response"]
    ]

    return fixtures_status
