import requests
from datetime import (
    datetime,
    timedelta,
)
from itertools import chain

from f_data_uploader.sql import (
    insert_matchday,
    insert_teams,
    insert_matches,
    get_matchdays,
    get_predictions,
    insert_results,
    update_matchday_status,
    has_one_spanish_match,
    matchday_exists,
    get_users_id,
    insert_predictions,
)
from f_data_uploader.results import evaluate_results
from f_data_uploader.logger import logger
from f_data_uploader.strings import clean_text
import f_data_uploader.cfg as cfg


def run_data_uploader():
    logger.info("Running data uploader...")

    logger.info("Getting next matchday...")
    next_matchday = get_next_matchday()
    logger.info("Finished getting next matchday")

    logger.info("Uploading teams...")
    upload_teams(next_matchday["partidos"])
    logger.info("Finished uploading teams")

    if not matchday_exists(next_matchday):
        logger.info("Uploading matchdays...")
        upload_matchdays(next_matchday)
        logger.info("Finished uploading matchdays")
    else:
        logger.info("Matchday already exists, skipping upload")

    logger.info("Uploading predictions...")
    upload_predictions()
    logger.info("Finished uploading predictions")

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

    team_names = [
        [match["local"], match["visitante"]] for match in matchday["partidos"]
    ]
    if not has_one_spanish_match(list(chain(*team_names))):
        logger.info("Matchday is not a spanish quiniela, skipping upload")
        return

    insert_matchday(matchday)
    insert_matches(matchday)
    logger.info(f"Successfully uploaded matchday {matchday['jornada']}")


def upload_predictions():
    params = {
        "firstResult": "0",
    }
    headers = {"Authorization": f"Basic {cfg.LOTERO_TOKEN}"}
    response = requests.get(
        f"{cfg.LOTERO_URL}/group",
        params=params,
        headers=headers,
    )
    response.raise_for_status()
    predictions = response.json()["boletos"]

    matchdays = [
        matchday["matchday"] for matchday in get_matchdays("NOT_STARTED")
    ]
    predictions_db = list()
    for prediction in predictions:
        matchday = int(prediction["sorteo"]["numJornada"])
        if matchday not in matchdays:
            continue

        lotero_user_id = None
        if "compartidoPor" in prediction:
            lotero_user_id = str(prediction["compartidoPor"]["clienteId"])

        if lotero_user_id:
            user_id = get_users_id(lotero_user_id)
        else:
            user_id = "3722aea7-3c82-416e-8996-90e6b3334cd2"

        combinaciones = prediction["apuesta"]["combinaciones"]
        match_15 = (
            combinaciones.pop()["linea"].split(":")[1].strip().replace(",", "-")
        )
        for col_num, combinacion in enumerate(combinaciones):
            line = combinacion["linea"].split(",")
            for match_num in range(14):
                line_fmt = line[match_num].replace("-E", "")
                predictions_db.append(
                    {
                        "user_id": user_id,
                        "season": "2024-2025",
                        "matchday": matchday,
                        "col_num": col_num,
                        "match_num": match_num,
                        "prediction": line_fmt,
                    }
                )

            predictions_db.append(
                {
                    "user_id": user_id,
                    "season": "2024-2025",
                    "matchday": matchday,
                    "col_num": col_num,
                    "match_num": 14,
                    "prediction": match_15,
                }
            )

    insert_predictions(predictions_db)


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

    matchdays = [*get_matchdays("IN_PROGRESS"), *get_matchdays("NOT_STARTED")]
    if not matchdays:
        logger.info("No matchdays in progress")
        return

    logger.info(f"Found matchdays to calculate results: {matchdays}")
    for matchday in matchdays:
        matchday_quinielas = [
            quiniela
            for quiniela in quinielas
            if int(quiniela["jornada"]) == matchday["matchday"]
        ]

        if len(matchday_quinielas) == 0:
            logger.info(
                "No results published yet, skipping results evaluation"
            )
            return

        quiniela = matchday_quinielas[0]
        users_predictions = get_predictions(matchday)

        user_results = evaluate_results(
            matchday, users_predictions, quiniela["partidos"]
        )
        insert_results(user_results)

        if quiniela["combinacion"]:
            update_matchday_status(matchday, "FINISHED")
            logger.info(f"Updated matchday {matchday["matchday"]} as finished")
        else:
            update_matchday_status(matchday, "IN_PROGRESS")


def upload_teams(matches: list[dict]):
    teams = list()
    for match in matches:
        home_team = (
            clean_text(match["local"]).replace(" ", "-").replace(".", ""),
            match["local"],
        )
        away_team = (
            clean_text(match["visitante"]).replace(" ", "-").replace(".", ""),
            match["visitante"],
        )

        teams.append(home_team)
        teams.append(away_team)

    insert_teams(teams)
