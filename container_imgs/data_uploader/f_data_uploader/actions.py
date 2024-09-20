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
    insert_results,
    mark_matchday_finished,
    get_home_chmps,
)
from f_data_uploader.results.results import evaluate_results
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
    upload_results(quinielas)
    logger.info("Finished calculating points")


def upload_matches(quinielas: list[dict]):

    teams = list()
    matchdays = list()
    matches = list()
    for quiniela in quinielas:
        quiniela_teams = list()
        for match in quiniela["partidos"]:
            quiniela_teams.append((match["idLocal"], match["local"]))
            quiniela_teams.append((match["idVisitante"], match["visitante"]))

        if not is_spanish_quiniela(quiniela_teams):
            continue

        teams.extend(quiniela_teams)
        matchdays.append(
            (
                quiniela["temporada"],
                quiniela["jornada"],
                "IN_PROGRESS" if not quiniela["combinacion"] else "FINISHED",
            )
        )
        matches.extend(
            [
                (
                    quiniela["temporada"],
                    quiniela["jornada"],
                    match_num,
                    match["idLocal"],
                    match["idVisitante"],
                )
                for match_num, match in enumerate(quiniela["partidos"])
            ]
        )

    insert_teams(teams)
    insert_matchdays(matchdays)
    insert_matches(matches)
    logger.info(f"Successfully uploaded {len(matchdays)} matchdays")


def is_spanish_quiniela(teams: list[tuple]):
    home_chmps = get_home_chmps([team[0] for team in teams])
    u_home_chmps = set(home_chmps)

    allowed_chmps = ["LA_LIGA", "LA_LIGA_2"]
    not_allowed = [
        u_home_chmp
        for u_home_chmp in u_home_chmps
        if u_home_chmp not in allowed_chmps
    ]
    if len(not_allowed) > 0:
        return False
    return True


def upload_results(quinielas: list[dict]):
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
        if len(users_predictions) == 0:
            continue

        user_results = evaluate_results(
            matchday, users_predictions, quiniela["partidos"]
        )
        insert_results(user_results)

        if "combinacion" in quiniela:
            mark_matchday_finished(matchday)
