import requests
from datetime import (
    datetime,
    timedelta,
)

from f_data_uploader.sql import (
    insert_matchdays,
    insert_matches,
    insert_teams,
    get_matchdays_in_progress,
    get_predictions,
    upload_points,
    mark_matchday_finished,
)
from f_data_uploader.logger import logger
import f_data_uploader.cfg as cfg


def run_data_uploader():
    logger.info("Running data uploader...")

    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
    params = {
        "game_id": "LAQU",
        "fechaInicioInclusiva": "20240901",
        "fechaFinInclusiva": tomorrow,
    }

    logger.info("Fetching data on quiniela API...")
    response = requests.get(cfg.QUINIELA_URL, params=params)
    response.raise_for_status()
    logger.info("Finished fetching data on quiniela API")

    quinielas = response.json()

    logger.info("Uploading matches...")
    upload_matches(quinielas)
    logger.info("Finished uploading matches")

    logger.info("Calculating points...")
    calculate_points(quinielas)
    logger.info("Finished calculating points")


def upload_matches(quinielas: list[dict]):

    teams = list()
    for quiniela in quinielas:
        for match in quiniela["partidos"]:
            teams.append((match["idLocal"], match["local"]))
            teams.append((match["idVisitante"], match["visitante"]))
    insert_teams(teams)

    matchdays = [
        (
            quiniela["temporada"],
            quiniela["jornada"],
            "IN_PROGRESS" if not quiniela["combinacion"] else "FINISHED",
        )
        for quiniela in quinielas
    ]
    insert_matchdays(matchdays)
    logger.info(f"Successfully uploaded {len(matchdays)} matchdays")

    for quiniela in quinielas:
        matches = [
            (
                quiniela["temporada"],
                quiniela["jornada"],
                match_num,
                match["idLocal"],
                match["idVisitante"],
            )
            for match_num, match in enumerate(quiniela["partidos"])
        ]
        insert_matches(matches)


def calculate_points(quinielas: list[dict]):
    matchdays = get_matchdays_in_progress()
    if not matchdays:
        logger.info("No matchdays in progress")
        return

    logger.info(f"Found matchdays in progress: {matchdays}")
    for matchday in matchdays:
        quiniela = [
            quiniela
            for quiniela in quinielas
            if int(quiniela["jornada"]) == matchday
        ][0]

        users_predictions = get_predictions(matchday)
        if len(users_predictions) == 0:
            continue

        user_scores = evaluate_user_points(
            users_predictions, quiniela["partidos"]
        )
        upload_points(user_scores)

        finished_matches = [
            match for match in quiniela["partidos"] if not match["signo"]
        ]
        if len(finished_matches) == 15:
            mark_matchday_finished(matchday)


def evaluate_user_points(
    users_predictions: list[dict],
    matches: dict[str],
) -> list[dict]:
    users_cols = dict()
    predictions_user_id = dict()
    for user_predictions in users_predictions:
        user_id = user_predictions["user_id"]
        if user_id not in predictions_user_id.keys():
            predictions_user_id[user_id] = dict()

        match_num = user_predictions["match_num"]
        predictions_user_id[user_id][match_num] = user_predictions[
            "predictions"
        ]

    for match_num, match in enumerate(matches):
        if match["signo"] is None:
            continue

        for user_id, predictions in predictions_user_id.items():
            if user_id not in users_cols.keys():
                users_cols[user_id] = [0, 0]
            for colI, col in enumerate(predictions[match_num].split("-")):
                if match["signo"] == col:
                    users_cols[user_id][colI] += 1

    user_points = list()
    for user_id, user_cols in users_cols.items():
        user_points.append(
            {
                "user_id": user_id,
                "matchday": user_predictions["matchday"],
                "season": user_predictions["season"],
                "points": max(user_cols[0], user_cols[1]),
            }
        )

    return user_points
