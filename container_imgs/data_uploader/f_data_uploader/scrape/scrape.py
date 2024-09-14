import re
import copy

from bs4 import BeautifulSoup

from f_scrapper.sql.teams import (
    get_teams_mapping,
)
from f_scrapper.strings import clean_text
from f_scrapper.logger import logger


def scrape_matchday(soup: BeautifulSoup) -> int:
    matchday_elem = soup.find("div", class_="numero-jornadas")
    matchday_number = None
    if matchday_elem:
        matchday_text = matchday_elem.text.strip()
        matchday_match = re.search(r"Jornada (\d+)", matchday_text)
        if matchday_match:
            matchday_number = matchday_match.group(1)
    return int(matchday_number)


def scrape_matches(soup: BeautifulSoup) -> list[dict[str, str]]:
    matches = list()

    partido_divs = soup.find_all("div", class_="partidos")

    logger.info(f"Found {len(partido_divs)} partido divs")

    for div in partido_divs:
        number_elem = div.find("strong", class_="numero-partido")
        if not number_elem:
            continue
        match_num = number_elem.text.strip().rstrip(".")

        team_elements = div.find_all("p", class_="equipo")
        if len(team_elements) != 2:
            continue

        home_team_name = team_elements[0].get("title", "").strip()
        away_team_name = team_elements[1].get("title", "").strip()

        if home_team_name and away_team_name:
            matches.append(
                {
                    "match_num": int(match_num),
                    "home_team_name": clean_text(home_team_name),
                    "away_team_name": clean_text(away_team_name),
                }
            )
        else:
            raise Exception(
                f"Match {match_num}: Could not find both team names"
            )

    return matches


def map_to_api(matches: list[dict]) -> list[dict]:
    teams_mapping = get_teams_mapping()

    name_to_id = {team["scrapper_name"]: team["id"] for team in teams_mapping}

    matches_team_id = copy.deepcopy(matches)
    for match in matches_team_id:
        home_team_name = match["home_team_name"]
        away_team_name = match["away_team_name"]

        match["home_team_id"] = name_to_id.get(home_team_name)
        if match["home_team_id"] is None:
            raise Exception(
                f"No mapping found for home team: {home_team_name}"
            )

        match["away_team_id"] = name_to_id.get(away_team_name)
        if match["away_team_id"] is None:
            raise Exception(
                f"No mapping found for away team: {away_team_name}"
            )

        match.pop("home_team_name", None)
        match.pop("away_team_name", None)

    return matches_team_id
