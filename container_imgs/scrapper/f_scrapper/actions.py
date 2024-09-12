from bs4 import BeautifulSoup
import requests

from f_scrapper.sql import (
    matchday_exists,
    upload_matches,
    get_matchdays_in_progress,
    get_predictions,
    get_matches,
    upload_points,
    mark_matchday_finished,
)
from f_scrapper.football_api import (
    map_matches,
    get_results,
)
from f_scrapper.logger import logger
from f_scrapper.scrape import (
    scrape_matches,
    map_to_api,
    scrape_matchday,
)
import f_scrapper.cfg as cfg


def run_scrapper():
    response = requests.get(cfg.QUINIELA_URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    matchday = scrape_matchday(soup)

    upload_matchday(matchday, soup)
    calculate_points()


def upload_matchday(matchday: int, soup: BeautifulSoup):
    if matchday_exists(matchday):
        logger.info("Matchday registered, skipping data upload")
        return

    logger.info("Matchday not registered yet, uploading data")

    matches = scrape_matches(soup)
    matches_team_id = map_to_api(matches)
    fixture_id_la_liga = map_matches(matches_team_id, 140)
    fixture_id_segunda = map_matches(fixture_id_la_liga, 141)
    upload_matches(fixture_id_segunda, matchday)


def calculate_points():
    matchdays = get_matchdays_in_progress()
    if not matchdays:
        logger.info("No matchdays in progress")
        return

    logger.info(f"Found matchdays in progress: {matchdays}")
    for matchday in matchdays:
        matches = get_matches(matchday)
        match_ids = [match["id"] for match in matches]
        results = get_results(match_ids)
        if not results:
            logger.info(f"Matches not started for matchday {matchday}")
            continue

        predictions = get_predictions(matchday)

        matches_by_num = {match["match_num"]: match["id"] for match in matches}
        user_scores = evaluate_user_points(
            predictions, matches_by_num, results
        )
        upload_points(user_scores)

        if len(results) == 15:
            mark_matchday_finished(matchday)


def evaluate_user_points(
    predictions: list[dict],
    matches_by_num: dict[int, int],
    results: dict[int, dict],
) -> list[dict]:
    user_points = list()
    for index, prediction in enumerate(predictions):
        match_id = matches_by_num.get(index + 1)
        result = results.get(match_id)

        scores = [0, 0]
        for cols in prediction["predictions"]:
            for colI, col in enumerate(cols.split("-")):
                if result["home"] > result["away"] and col == "1":
                    scores[colI] += 1
                    continue

                if result["home"] == result["away"] and col == "X":
                    scores[colI] += 1
                    continue

                if result["home"] < result["away"] and col == "2":
                    scores[colI] += 1
                    continue

        user_points.append(
            {
                "user_id": prediction["user_id"],
                "matchday": prediction["matchday"],
                "points": max(scores[0], scores[1]),
            }
        )

    return user_points
