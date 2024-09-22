from dotenv import load_dotenv
import requests
from datetime import (
    datetime,
    timedelta,
)

from f_data_uploader.sql import (
    get_predictions,
    insert_results,
    mark_matchday_finished,
)
from f_data_uploader.results.results import evaluate_results
from f_data_uploader.logger import logger
import f_data_uploader.cfg as cfg


def recalculate_matchday(matchday: dict):
    logger.info("Running data uploader...")

    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
    params = {
        "game_id": "LAQU",
        "fechaInicioInclusiva": "20240901",
        "fechaFinInclusiva": tomorrow,
    }

    response = requests.get(cfg.QUINIELA_URL, params=params)
    response.raise_for_status()
    logger.info("Finished fetching data on quiniela API")

    quiniela = [
        quiniela
        for quiniela in response.json()
        if int(quiniela["jornada"]) == matchday["matchday"]
    ][0]

    users_predictions = get_predictions(matchday)

    user_results = evaluate_results(
        matchday, users_predictions, quiniela["partidos"]
    )
    insert_results(user_results)

    if "combinacion" in quiniela:
        mark_matchday_finished(matchday)


load_dotenv(".env")

if __name__ == "__main__":
    recalculate_matchday({"season": "2024-2025", "matchday": 9})
