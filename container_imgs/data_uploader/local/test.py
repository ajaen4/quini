import requests

import f_data_uploader.cfg as cfg


match_ids_param = "1208608-1208609"
params = {"ids": match_ids_param}
headers = {"x-rapidapi-key": cfg.FOOT_API_TOKEN}
response = requests.get(
    f"{cfg.FOOT_API_URL}/fixtures",
    params=params,
    headers=headers,
)
response.raise_for_status()
data = response.json()
