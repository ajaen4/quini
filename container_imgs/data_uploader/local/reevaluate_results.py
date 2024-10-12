from dotenv import load_dotenv
import requests
from datetime import (
    datetime,
    timedelta,
)

from f_data_uploader.sql import (
    get_matchday_points,
    insert_results,
    update_matchday_status,
)
from f_data_uploader.results.results import evaluate_results
from f_data_uploader.logger import logger
import f_data_uploader.cfg as cfg


def reevaluate_results(matchday: dict):
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
    params = {
        "game_id": "LAQU",
        "fechaInicioInclusiva": "20240901",
        "fechaFinInclusiva": tomorrow,
    }

    response = requests.get(
        f"{cfg.QUINIELA_URL}/buscadorSorteos", params=params
    )
    response.raise_for_status()
    quinielas = response.json()

    quiniela = [
        quiniela
        for quiniela in quinielas
        if int(quiniela["jornada"]) == matchday["matchday"]
    ][0]

    if len(quiniela) == 0:
        logger.info("No results published yet, skipping results evaluation")
        return

    matchday_points = get_matchday_points(matchday)
    user_results = evaluate_results(matchday, matchday_points)
    insert_results(user_results)

    if quiniela["combinacion"]:
        update_matchday_status(matchday, "FINISHED")
        logger.info(f"Updated matchday {matchday["matchday"]} as finished")
    else:
        update_matchday_status(matchday, "IN_PROGRESS")


load_dotenv(".env")

if __name__ == "__main__":
    reevaluate_results({"season": "2024-2025", "matchday": 13})
