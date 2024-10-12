package db

import "github.com/jackc/pgx/v5/pgtype"

func GetMatchdayInProg() (int32, error) {
	db := New()

	var maxMatchday pgtype.Int4
	err := db.QueryRow(
		`SELECT MAX(matchday) as max_matchday
		FROM bavariada.matchdays
		WHERE season = '2024-2025'
		AND status = 'IN_PROGRESS';`,
	).Scan(&maxMatchday)
	if err != nil {
		return 0, err
	}

	return maxMatchday.Int32, nil
}
