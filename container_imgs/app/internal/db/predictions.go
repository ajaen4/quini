package db

import (
	"github.com/jackc/pgx/v5/pgtype"
)

type UserPredictions struct {
	UserName    string          `json:"user_name"`
	Predictions [][]string      `json:"predictions"`
	IsCorrect   [][]pgtype.Bool `json:"is_correct"`
	IsElige8    [][]pgtype.Bool `json:"is_elige8"`
}

func GetUserPredictions(matchday int32) (map[string]UserPredictions, error) {
	db := New()

	rows, err := db.Query(
		`WITH predictions_per_user_match AS (
			SELECT
				user_id,
				match_num,
				array_agg(prediction ORDER BY col_num) as predictions,
				array_agg(is_correct ORDER BY col_num) as is_correct,
				array_agg(is_elige8 ORDER BY col_num) as is_elige8
			FROM bavariada.predictions
			WHERE season = '2024-2025' AND matchday = $1
			GROUP BY user_id, match_num
		)
		SELECT
			users.id as user_id,
			COALESCE(COALESCE(users.raw_user_meta_data->>'display_name', users.email), users.email) AS display_name,
			array_agg(predictions_per_user_match.predictions ORDER BY predictions_per_user_match.match_num) as predictions,
			array_agg(predictions_per_user_match.is_correct ORDER BY predictions_per_user_match.match_num) as is_correct,
			array_agg(predictions_per_user_match.is_elige8 ORDER BY predictions_per_user_match.match_num) as is_elige8
		FROM predictions_per_user_match
		LEFT JOIN auth.users users ON predictions_per_user_match.user_id = users.id
		GROUP BY users.id, COALESCE(COALESCE(users.raw_user_meta_data->>'display_name', users.email), users.email);`,
		matchday,
	)
	if err != nil {
		return map[string]UserPredictions{}, err
	}
	defer rows.Close()

	usersPredictions := map[string]UserPredictions{}
	for rows.Next() {
		userPredictions := UserPredictions{}
		var userId string
		err = rows.Scan(
			&userId,
			&userPredictions.UserName,
			&userPredictions.Predictions,
			&userPredictions.IsCorrect,
			&userPredictions.IsElige8,
		)
		if err != nil {
			return map[string]UserPredictions{}, err
		}
		usersPredictions[userId] = userPredictions
	}

	return usersPredictions, nil
}
