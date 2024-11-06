from datetime import datetime, timedelta
import requests

import f_data_uploader.cfg as cfg


def get_quiniela(matchday: int) -> list:
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
    params = {
        "game_id": "LAQU",
        "fechaInicioInclusiva": "20240901",
        "fechaFinInclusiva": tomorrow,
    }

    response = requests.get(
        f"{cfg.LOTERIAS_URL}/buscadorSorteos", params=params
    )
    response.raise_for_status()
    quinielas = response.json()

    for quiniela in quinielas:
        if matchday == int(quiniela["jornada"]):
            return quiniela["partidos"]

    raise Exception("Matchday not found in loterias API")
