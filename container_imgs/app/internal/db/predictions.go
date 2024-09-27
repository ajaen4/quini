package db

import (
	"fmt"
)

type UserPredictions struct {
	UserName    string     `json:"user_name"`
	Predictions [][]string `json:"predictions"`
}

func GetUserPredictions(maxMatchday int32) ([]UserPredictions, error) {
	db := New()

	rows, err := db.Query(
		fmt.Sprintf(
			`WITH predictions_per_user_match AS (
				SELECT
					user_id,
					match_num,
					array_agg(prediction ORDER BY col_num) as predictions
				FROM bavariada.predictions
				WHERE season = '2024-2025' AND matchday = %d
				GROUP BY user_id, match_num
			)
			SELECT
				users.raw_user_meta_data->>'display_name' AS display_name,
				array_agg(predictions_per_user_match.predictions ORDER BY predictions_per_user_match.match_num) as predictions
			FROM predictions_per_user_match
			LEFT JOIN auth.users users ON predictions_per_user_match.user_id = users.id
			GROUP BY users.id, users.raw_user_meta_data->>'display_name';`,
			maxMatchday,
		),
	)
	if err != nil {
		return []UserPredictions{}, err
	}

	usersPredictions := []UserPredictions{}
	for rows.Next() {
		userPredictions := UserPredictions{}
		err = rows.Scan(&userPredictions.UserName, &userPredictions.Predictions)
		if err != nil {
			return []UserPredictions{}, err
		}
		usersPredictions = append(usersPredictions, userPredictions)
	}
	return usersPredictions, nil
}
