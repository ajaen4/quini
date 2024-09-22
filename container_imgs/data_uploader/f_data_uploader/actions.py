import requests
from datetime import (
    datetime,
    timedelta,
)
from itertools import chain

from f_data_uploader.sql import (
    insert_matchday,
    insert_matches,
    get_matchdays_in_progress,
    get_predictions,
    insert_results,
    mark_matchday_finished,
    is_spanish_league,
    matchday_exists,
)
from f_data_uploader.results.results import evaluate_results
from f_data_uploader.logger import logger
import f_data_uploader.cfg as cfg


def run_data_uploader():
    logger.info("Running data uploader...")

    logger.info("Getting next matchday...")
    next_matchday = get_next_matchday()
    logger.info("Finished getting next matchday")

    logger.info("Uploading matchdays...")
    upload_matchdays(next_matchday)
    logger.info("Finished uploading matchdays")

    logger.info("Calculating points...")
    upload_results()
    logger.info("Finished calculating points")

    logger.info("Finished running data uploader")


def get_next_matchday():
    params = {
        "game_id": "LAQU",
        "num": "1",
    }

    response = requests.get(
        f"{cfg.QUINIELA_URL}/proximosv3",
        params=params,
    )
    response.raise_for_status()
    next_matchday = response.json()[0]

    matchday_date = datetime.strptime(
        next_matchday["fecha"], "%Y-%m-%d %H:%M:%S"
    ).strftime("%Y%m%d")
    params = {
        "game_id": "LAQU",
        "fecha_sorteo": matchday_date,
    }
    response = requests.get(
        f"{cfg.QUINIELA_URL}/fechav3",
        params=params,
    )
    response.raise_for_status()

    return response.json()[0]


def upload_matchdays(matchday: dict):
    logger.info(f"Next matchday: {matchday["jornada"]}")

    if matchday_exists(matchday):
        logger.info("Matchday already exists, skipping upload")
        return

    team_names = [
        [match["local"], match["visitante"]] for match in matchday["partidos"]
    ]
    if not is_spanish_league(list(chain(*team_names))):
        logger.info("Matchday is not a spanish quiniela, skipping upload")
        return

    insert_matchday(matchday)
    insert_matches(matchday)
    logger.info(f"Successfully uploaded matchday {matchday['jornada']}")


def upload_predictions():
    params = {
        "firstResult": "0",
    }
    headers = {
        "Authorization": f"Basic {cfg.LOTERO_TOKEN}"
    }
    response = requests.get(
        f"{cfg.LOTERO_URL}/group",
        params=params,
        headers=headers,
    )
    response.raise_for_status()
    predictions = response.json()


def upload_results():
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

    matchdays = get_matchdays_in_progress()
    if not matchdays:
        logger.info("No matchdays in progress")
        return

    logger.info(f"Found matchdays in progress: {matchdays}")
    for matchday in matchdays:
        quiniela = [
            quiniela
            for quiniela in quinielas
            if int(quiniela["jornada"]) == matchday["matchday"]
        ][0]

        users_predictions = get_predictions(matchday)

        user_results = evaluate_results(
            matchday, users_predictions, quiniela["partidos"]
        )
        insert_results(user_results)

        if quiniela["combinacion"]:
            mark_matchday_finished(matchday)
            logger.info(f"Marked matchday {matchday["matchday"]} as finished")
