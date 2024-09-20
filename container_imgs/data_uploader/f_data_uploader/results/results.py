from collections import defaultdict

from f_data_uploader.sql.users import get_users


def evaluate_results(
    matchday: dict,
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

            correct_pred = match["signo"].strip()

            # Pleno al 15
            if match_num == 14 and predictions[match_num] == correct_pred:
                users_cols[user_id] = [
                    users_cols[user_id][0] + 1,
                    users_cols[user_id][1] + 1,
                ]
                continue

            for colI, col in enumerate(predictions[match_num].split("-")):
                if correct_pred == col:
                    users_cols[user_id][colI] += 1

    user_results = list()
    for user_id, user_cols in users_cols.items():
        user_results.append(
            {
                "user_id": user_id,
                "matchday": user_predictions["matchday"],
                "season": user_predictions["season"],
                "points": max(user_cols[0], user_cols[1]),
            }
        )

    user_ids = [user_result["user_id"] for user_result in user_results]
    db_users = get_users()
    for db_user in db_users:
        if db_user["id"] not in user_ids:
            user_results.append(
                {
                    "user_id": db_user["id"],
                    "matchday": matchday["matchday"],
                    "season": matchday["season"],
                    "points": 0,
                }
            )

    return evaluate_debt(user_results)


def evaluate_debt(user_results: list[dict]) -> list[dict]:
    grouped_results = defaultdict(list)
    for result in user_results:
        key = (result["matchday"], result["season"])
        grouped_results[key].append(result)

    result = []
    for group in grouped_results.values():
        sorted_group = sorted(group, key=lambda x: x["points"])

        if len(sorted_group) == 1:
            sorted_group[0]["debt_euros"] = 3.0
            continue
        elif len(sorted_group) == 2:
            sorted_group[0]["debt_euros"] = 3.0
            sorted_group[1]["debt_euros"] = 2.0
            continue

        min_points = sorted_group[0]["points"]
        rest = [
            item["points"]
            for item in sorted_group
            if item["points"] > min_points
        ]

        if len(rest) == 0:
            tie_count = sum(
                1 for item in sorted_group if item["points"] == min_points
            )
            tie_debt = 5.0 / tie_count
            for item in sorted_group:
                item["debt_euros"] = (
                    tie_debt if item["points"] == min_points else 0.0
                )
        else:
            sorted_group[0]["debt_euros"] = 3.0
            sorted_group[1]["debt_euros"] = 2.0
            for item in sorted_group[2:]:
                item["debt_euros"] = 0.0

        result.extend(sorted_group)

    return result
