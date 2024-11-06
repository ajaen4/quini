from dotenv import load_dotenv
import requests
from itertools import chain

from f_data_uploader.sql import (
    has_one_spanish_match,
    insert_matches,
)
from f_data_uploader.actions import (
    upload_teams,
)
from f_data_uploader.logger import logger
import f_data_uploader.cfg as cfg


def reupload_matchday(matchday_date: str):
    params = {
        "game_id": "LAQU",
        "fecha_sorteo": matchday_date,
    }
    response = requests.get(
        f"{cfg.LOTERIAS_URL}/fechav3",
        params=params,
    )
    response.raise_for_status()

    matchday = response.json()[0]

    team_names = [
        [match["local"], match["visitante"]] for match in matchday["partidos"]
    ]
    if not has_one_spanish_match(list(chain(*team_names))):
        logger.info("Matchday is not a spanish quiniela, skipping upload")
        return

    upload_teams(matchday["partidos"])
    insert_matches(matchday)


load_dotenv(".env")

if __name__ == "__main__":
    reupload_matchday(matchday_date="20240915")
