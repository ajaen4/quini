import requests
from datetime import (
    datetime,
    timedelta,
)

from f_data_uploader.sql import (
    insert_matchday,
    insert_teams,
    insert_matches,
    get_matchdays,
    get_matchday_points,
    insert_results,
    update_matchday_status,
    has_one_spanish_match,
    matchday_exists,
    get_user_id,
    insert_predictions,
    insert_prices,
    update_predictions,
    insert_predictions_stats,
)
from f_data_uploader.football_api import add_match_ids
from f_data_uploader.results import evaluate_results
from f_data_uploader.logger import logger
from f_data_uploader.strings import team_name_to_loterias_id
import f_data_uploader.cfg as cfg


def run_data_uploader():
    logger.info("Running data uploader...")

    logger.info("Getting next matchday...")
    next_matchday = get_next_matchday()
    logger.info("Finished getting next matchday")

    if next_matchday is None:
        logger.info("Matchday not ready, skipping upload")
    elif matchday_exists(next_matchday):
        logger.info("Matchday already exists, skipping upload")
    elif not has_one_spanish_match(next_matchday["partidos"]):
        logger.info("Matchday is not a spanish quiniela, skipping upload")
    else:
        logger.info("Uploading matchdays...")
        upload_matchday(next_matchday)
        logger.info("Finished uploading matchdays")

    if next_matchday is not None and matchday_exists(next_matchday):
        logger.info("Fetching predictions statistics...")
        upload_predictions_stats(next_matchday)
        logger.info("Finished fetching predictions statistics")

    logger.info("Uploading predictions...")
    upload_predictions()
    logger.info("Finished uploading predictions")

    logger.info("Checking correct predictions...")
    upload_is_correct()
    logger.info("Finished checking correct predictions")

    logger.info("Calculating points...")
    upload_results()
    logger.info("Finished calculating points")

    logger.info("Calculating prices earned...")
    upload_prices()
    logger.info("Finished calculating prices earned")

    logger.info("Finished running data uploader")


def get_next_matchday() -> dict:
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

    if next_matchday["cierre"] is None:
        return None

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

    complete_matchday = response.json()[0]
    return {
        **complete_matchday,
        "start_datetime": next_matchday["cierre"],
    }


def upload_matchday(matchday: dict):
    logger.info(f"Next matchday: {matchday['jornada']}")

    insert_matchday(matchday)
    matchday_match_ids = add_match_ids(matchday)
    insert_matches(matchday_match_ids)
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
            user_id = get_user_id(lotero_user_id)
        else:
            user_id = "3722aea7-3c82-416e-8996-90e6b3334cd2"

        combinaciones = prediction["apuesta"]["combinaciones"]
        match_15 = (
            combinaciones.pop()["linea"]
            .split(":")[1]
            .strip()
            .replace(",", "-")
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
                        "is_elige8": "E" in line[match_num],
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
                    "is_elige8": False,
                }
            )

    insert_predictions(predictions_db)


def upload_is_correct():
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

    matchdays = [*get_matchdays("IN_PROGRESS")]
    if not matchdays:
        logger.info("No matchdays in progress")
        return

    logger.info(f"Found matchdays: {matchdays}")
    for matchday in matchdays:
        matchday_quinielas = [
            quiniela
            for quiniela in quinielas
            if int(quiniela["jornada"]) == matchday["matchday"]
        ]

        if len(matchday_quinielas) == 0:
            logger.info("No results published yet, skipping is_correct upload")
            return

        quiniela = matchday_quinielas[0]
        match_results = list()
        for match_num, match in enumerate(quiniela["partidos"]):
            if match["signo"] is None:
                continue

            match_results.append(
                {
                    "season": "2024-2025",
                    "matchday": matchday["matchday"],
                    "match_num": match_num,
                    "result": match["signo"].strip(),
                }
            )

        update_predictions(match_results)


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

    logger.info(f"Found matchdays: {matchdays}")
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
        matchday_points = get_matchday_points(matchday)
        user_results = evaluate_results(matchday, matchday_points)
        insert_results(user_results)

        if quiniela["combinacion"]:
            update_matchday_status(matchday, "FINISHED")
            logger.info(f"Updated matchday {matchday['matchday']} as finished")
        else:
            update_matchday_status(matchday, "IN_PROGRESS")


def upload_teams(matches: list[dict]):
    teams = list()
    for match in matches:
        home_team = (
            team_name_to_loterias_id(match["local"]),
            match["local"],
        )
        away_team = (
            team_name_to_loterias_id(match["visitante"]),
            match["visitante"],
        )

        teams.append(home_team)
        teams.append(away_team)

    insert_teams(teams)


def upload_prices():
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
    results = response.json()["boletos"]

    matchdays = [
        matchday["matchday"] for matchday in get_matchdays("FINISHED")
    ]
    prices = list()
    for result in results:
        matchday = int(result["sorteo"]["numJornada"])
        if matchday not in matchdays or "premio" not in result:
            continue

        lotero_user_id = None
        if "compartidoPor" in result:
            lotero_user_id = str(result["compartidoPor"]["clienteId"])

        if lotero_user_id == "6476125":
            continue
        elif lotero_user_id:
            user_id = get_user_id(lotero_user_id)
        else:
            user_id = "3722aea7-3c82-416e-8996-90e6b3334cd2"

        prices.append(
            {
                "user_id": user_id,
                "season": "2024-2025",
                "matchday": matchday,
                "price_euros": result["premio"],
            }
        )

    insert_prices(prices)


def upload_predictions_stats(matchday: dict):
    season = int(matchday["anyo"])
    season_matchday = {
        "matchday": matchday["jornada"],
        "season": f"{season}-{season+1}",
    }

    params = {
        "jornada": season_matchday["matchday"],
        "temporada": season,
    }
    response = requests.get(
        f"{cfg.QUINIELA_URL}/estadisticas",
        params=params,
    )
    response.raise_for_status()
    statistics = response.json()

    if isinstance(statistics, dict):
        statistics.pop("fecha_actualizacion")
        insert_predictions_stats(season_matchday, statistics)
    else:
        logger.info("Statistics not available yet")
