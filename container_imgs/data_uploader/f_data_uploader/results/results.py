from collections import defaultdict

from f_data_uploader.sql import get_users


def evaluate_results(
    matchday: dict,
    users_predictions: list[dict],
    matches: dict[str],
) -> list[dict]:
    users_cols = dict()

    for match_num, match in enumerate(matches):
        if match["signo"] is None:
            continue

        for user_predictions in users_predictions:
            user_id = user_predictions["user_id"]
            num_cols = len(user_predictions["match_predictions"][0])
            if user_id not in users_cols.keys():
                users_cols[user_id] = [0] * num_cols

            correct_pred = match["signo"].strip()
            pred = user_predictions["match_predictions"][match_num]

            for colI, col in enumerate(pred):
                if correct_pred.lower() == col.lower():
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

        LAST_DEBT = 3.0
        SECOND_LAST_DEBT = 2.0
        if len(sorted_group) == 1:
            sorted_group[0]["debt_euros"] = LAST_DEBT
            continue

        min_points = sorted_group[0]["points"]
        min_points_users = [
            item for item in sorted_group if item["points"] == min_points
        ]

        # If tied for last place divide the whole debt
        if len(min_points_users) > 1:
            tie_debt = (LAST_DEBT + SECOND_LAST_DEBT) / len(min_points_users)
            for user in min_points_users:
                user["debt_euros"] = tie_debt

            fill_debt_0(sorted_group)
            result.extend(sorted_group)
            continue

        # If no tie for last place give last place debt
        sorted_group[0]["debt_euros"] = LAST_DEBT
        second_min_points = sorted_group[1]["points"]
        second_min_points_users = [
            item
            for item in sorted_group
            if item["points"] == second_min_points
        ]

        # If tie for second last place, divide the second last debt
        # between users tied
        if len(second_min_points_users) > 1:
            tie_debt = SECOND_LAST_DEBT / len(second_min_points_users)
            for user in second_min_points_users:
                user["debt_euros"] = tie_debt
        # If no tie, give second last its debt
        else:
            sorted_group[1]["debt_euros"] = SECOND_LAST_DEBT

        fill_debt_0(sorted_group)
        result.extend(sorted_group)

    return result


def fill_debt_0(sorted_group: list[dict]) -> list[dict]:
    for user in sorted_group:
        if "debt_euros" not in user:
            user["debt_euros"] = 0.0
    return sorted_group
