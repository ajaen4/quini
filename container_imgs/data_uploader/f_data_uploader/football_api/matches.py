import requests
import copy

import f_data_uploader.cfg as cfg
from f_data_uploader.sql import get_team_id
from f_data_uploader.strings import get_loterias_id
from f_data_uploader.loterias_api import get_quiniela


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


def get_matches_status(matchday: int, matches: list[str]):
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
    fixtures_score = {
        fixture["fixture"]["id"]: {
            "status": fixture["fixture"]["status"],
            "goals": fixture["goals"],
        }
        for fixture in data["response"]
    }

    quiniela = get_quiniela(matchday)

    fixtures_sign = list()
    for match in matches:
        fixture = fixtures_score[match["id"]]

        # Match postponed and loterias has results
        if fixture["status"]["short"] == "PST" and quiniela is not None:
            fixtures_sign.append(quiniela[match["match_num"]].strip())
            continue
        # Match postponed but loterias with no results yet
        elif fixture["status"]["short"] == "PST":
            fixtures_sign.append(None)
            continue

        if fixture["goals"]["home"] is None:
            fixtures_sign.append(None)
            continue

        if fixture["goals"]["home"] > fixture["goals"]["away"]:
            fixtures_sign.append("1")
        elif fixture["goals"]["home"] == fixture["goals"]["away"]:
            fixtures_sign.append("X")
        else:
            fixtures_sign.append("2")

    return fixtures_sign
