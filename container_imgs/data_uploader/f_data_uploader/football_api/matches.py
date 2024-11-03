import requests
import copy

import f_data_uploader.cfg as cfg
from f_data_uploader.sql import get_team_id
from f_data_uploader.strings import team_name_to_loterias_id


def add_match_ids(matchday: dict) -> dict:
    matchday_copy = copy.deepcopy(matchday)

    headers = {"x-rapidapi-key": cfg.FOOT_API_TOKEN}
    for match in matchday_copy["partidos"]:
        home_id = get_team_id(team_name_to_loterias_id(match["local"]))
        away_id = get_team_id(team_name_to_loterias_id(match["visitante"]))

        url = f"{cfg.FOOT_API_URL}/fixtures/headtohead?h2h={home_id}-{away_id}&next=1"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        match_info = response.json()["response"][0]["fixture"]

        match["id"] = match_info["id"]
        match["home_id"] = home_id
        match["away_id"] = away_id

    return matchday_copy
