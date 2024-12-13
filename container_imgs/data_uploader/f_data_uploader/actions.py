import requests
from datetime import (
    datetime,
)
from zoneinfo import ZoneInfo

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
    get_matches,
    update_matches,
)
from f_data_uploader.football_api import add_match_ids, get_matches_status
from f_data_uploader.loterias_api import get_quiniela
from f_data_uploader.results import evaluate_results
from f_data_uploader.logger import logger
from f_data_uploader.strings import get_loterias_id
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

    logger.info("Updating matches status...")
    update_matches_status()
    logger.info("Updated matches status")

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
        f"{cfg.LOTERIAS_URL}/proximosv3",
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
        f"{cfg.LOTERIAS_URL}/fechav3",
        params=params,
    )
    response.raise_for_status()

    complete_matchday = response.json()[0]
    start_datetime = datetime.strptime(
        next_matchday["cierre"], "%Y-%m-%d %H:%M:%S"
    ).replace(tzinfo=ZoneInfo("Europe/Madrid"))
    return {
        **complete_matchday,
        "start_datetime": start_datetime,
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
            user_id = "39ecabed-4917-4774-bc64-f9219dec455a"

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


def update_matches_status():
    matchdays = [*get_matchdays("IN_PROGRESS"), *get_matchdays("NOT_STARTED")]
    for matchday in matchdays:
        matches = get_matches(matchday["matchday"])
        matches_status = get_matches_status(matches)
        update_matches(matches_status)


def upload_is_correct():
    matchdays = [*get_matchdays("IN_PROGRESS"), *get_matchdays("NOT_STARTED")]
    if not matchdays:
        logger.info("No matchdays in progress")
        return

    logger.info(f"Found matchdays: {matchdays}")
    for matchday in matchdays:
        matches = get_matches(matchday["matchday"])
        quiniela = get_quiniela(matchday["matchday"])

        matches_status = evaluate_matches(quiniela, matches)
        match_results = list()
        for match_status in matches_status:
            match_results.append(
                {
                    "season": "2024-2025",
                    "matchday": matchday["matchday"],
                    "match_num": match_status["match_num"],
                    "result": match_status["sign"],
                }
            )

        update_predictions(match_results)


def evaluate_matches(quiniela: dict, matches: dict):
    fixtures_sign = list()
    for match in matches:
        # Match postponed and loterias has results
        if match["status"] == "PST" and quiniela[match["match_num"]]["signo"]:
            fixtures_sign.append(
                {
                    "match_num": match["match_num"],
                    "sign": quiniela[match["match_num"]]["signo"].strip(),
                }
            )
            continue
        # Match postponed but loterias with no results yet
        elif match["status"] == "PST":
            continue

        if match["status"] != "FT":
            continue

        # Pleno al 15
        if match["match_num"] == 14:
            home_goals = (
                match["home_goals"] if match["home_goals"] < 2 else "M"
            )
            away_goals = (
                match["away_goals"] if match["away_goals"] < 2 else "M"
            )
            fixtures_sign.append(
                {
                    "match_num": match["match_num"],
                    "sign": f"{home_goals}-{away_goals}",
                }
            )
        # Rest of matches
        elif match["home_goals"] > match["away_goals"]:
            fixtures_sign.append(
                {"match_num": match["match_num"], "sign": "1"}
            )
        elif match["home_goals"] == match["away_goals"]:
            fixtures_sign.append(
                {"match_num": match["match_num"], "sign": "X"}
            )
        else:
            fixtures_sign.append(
                {"match_num": match["match_num"], "sign": "2"}
            )

    return fixtures_sign


def upload_results():
    matchdays = [*get_matchdays("IN_PROGRESS"), *get_matchdays("NOT_STARTED")]
    if not matchdays:
        logger.info("No matchdays in progress")
        return

    logger.info(f"Found matchdays: {matchdays}")
    for matchday in matchdays:
        now = datetime.now(tz=ZoneInfo("UTC"))
        if matchday["start_datetime"] > now:
            continue

        matchday_points = get_matchday_points(matchday)
        user_results = evaluate_results(matchday, matchday_points)
        insert_results(user_results)

        matches = get_matches(matchday["matchday"])

        if matchday["status"] == "IN_PROGRESS" and not any(
            match["status"] != "FT" and match["status"] != "PST"
            for match in matches
        ):
            update_matchday_status(matchday, "FINISHED")
            logger.info(f"Updated matchday {matchday['matchday']} as finished")
        elif matchday["status"] == "NOT_STARTED" and any(
            match["status"] != "NS" and match["status"] != "PST"
            for match in matches
        ):
            update_matchday_status(matchday, "IN_PROGRESS")


def upload_teams(matches: list[dict]):
    teams = list()
    for match in matches:
        home_team = (
            get_loterias_id(match["local"]),
            match["local"],
        )
        away_team = (
            get_loterias_id(match["visitante"]),
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

    matchdays = [get_matchdays("FINISHED", limit=1)[0]["matchday"]]
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
        f"{cfg.LOTERIAS_URL}/estadisticas",
        params=params,
    )
    response.raise_for_status()
    statistics = response.json()

    if isinstance(statistics, dict):
        statistics.pop("fecha_actualizacion")
        insert_predictions_stats(season_matchday, statistics)
    else:
        logger.info("Statistics not available yet")
