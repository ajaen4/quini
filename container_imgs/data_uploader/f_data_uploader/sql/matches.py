from datetime import datetime
from zoneinfo import ZoneInfo

from f_data_uploader.database import db
from f_data_uploader.logger import logger
from f_data_uploader.strings import get_loterias_id


def insert_matches(matchday: dict):
    cur = db.get_conn().cursor()
    values = list()
    for match_num, match in enumerate(matchday["partidos"]):
        match_date = datetime.strptime(
            match["fecha"], "%Y/%m/%d %H:%M:%S"
        ).replace(tzinfo=ZoneInfo("Europe/Madrid"))

        values.append(
            (
                match["id"],
                matchday["temporada"],
                int(matchday["jornada"]),
                match_num,
                match_date,
                match["home_id"],
                match["away_id"],
            )
        )

    cur.executemany(
        """
        INSERT INTO bavariada.matches (
            id,
            status,
            season,
            matchday,
            match_num,
            kickoff_datetime,
            home_team_id,
            away_team_id
        )
        VALUES (
            %s,
            'NS',
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        values,
    )
    cur.close()


def update_matches(matches: list):
    cur = db.get_conn().cursor()
    values = list()
    for match in matches:
        values.append(
            (
                match["status"],
                match["home_goals"],
                match["away_goals"],
                match["minutes"],
                match["id"],
            )
        )

    cur.executemany(
        """
        UPDATE bavariada.matches
        SET
            status = %s,
            home_goals = %s,
            away_goals = %s,
            minutes=%s
        WHERE
            id = %s
        """,
        values,
    )
    cur.close()


def get_matches(matchday: int) -> list[dict]:
    cur = db.get_conn().cursor()
    cur.execute(
        """
        SELECT *
        FROM bavariada.matches m
        WHERE m.matchday = %s
        ORDER BY m.match_num
        """,
        (matchday,),
    )

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    matches = [
        {columns[i]: value for i, value in enumerate(row)} for row in rows
    ]

    cur.close()

    return matches


def has_one_spanish_match(matches: list[dict]) -> bool:
    cur = db.get_conn().cursor()
    team_ids = set()
    for match in matches:
        team_ids.add(get_loterias_id(match["local"]))
        team_ids.add(get_loterias_id(match["visitante"]))

    cur.execute(
        """
        SELECT loterias_id, league_id
        FROM bavariada.teams
        WHERE loterias_id = ANY(%s)
        """,
        (list(team_ids),),
    )
    team_championships = {str(row[0]): row[1] for row in cur.fetchall()}

    cur.close()

    LA_LIGA_ID = 140
    for match in matches:
        local_league_id = team_championships.get(
            get_loterias_id(match["local"])
        )
        away_league_id = team_championships.get(
            get_loterias_id(match["visitante"])
        )

        if local_league_id == LA_LIGA_ID and away_league_id == LA_LIGA_ID:
            logger.info("Found at least one la liga match")
            return True

    logger.info("Didn't find any la liga match, skipping matchday upload")

    return False
