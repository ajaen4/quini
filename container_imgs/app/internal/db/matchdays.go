package db

import (
	"slices"

	"github.com/jackc/pgx/v5/pgtype"
)

func GetMatchdayInProg() (int32, error) {
	db := New()

	var maxMatchday pgtype.Int4
	err := db.QueryRow(
		`SELECT MAX(matchday) as max_matchday
		FROM bavariada.matchdays
		WHERE season = '2024-2025'
		AND status = 'IN_PROGRESS'
		OR (status = 'NOT_STARTED' AND start_datetime < (CURRENT_TIMESTAMP + INTERVAL '2 hours'));`,
	).Scan(&maxMatchday)
	if err != nil {
		return 0, err
	}

	return maxMatchday.Int32, nil
}

func GetMatchdays() ([]int, error) {
	db := New()

	rows, err := db.Query(
		`SELECT matchday
		FROM bavariada.matchdays
		WHERE season = '2024-2025'
		AND (status = 'IN_PROGRESS'
		OR status = 'FINISHED')
		ORDER BY matchday DESC;`,
	)
	if err != nil {
		return []int{}, err
	}

	lastMatchdays := []int{}
	for rows.Next() {
		var matchday int32
		err = rows.Scan(&matchday)
		if err != nil {
			return []int{}, err
		}
		lastMatchdays = append(lastMatchdays, int(matchday))
	}
	slices.Reverse(lastMatchdays)
	return lastMatchdays, nil
}

func TotalMatchdays() (int32, error) {
	db := New()

	var totalMatchdays pgtype.Int4
	err := db.QueryRow(
		`SELECT count(*)
		FROM bavariada.matchdays
		WHERE season = '2024-2025'
		AND (
			status = 'IN_PROGRESS'
			OR status = 'FINISHED'
		);`,
	).Scan(&totalMatchdays)
	if err != nil {
		return 0, err
	}

	return totalMatchdays.Int32, nil
}
