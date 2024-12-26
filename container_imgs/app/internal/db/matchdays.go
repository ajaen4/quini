package db

import (
	"slices"

	"github.com/jackc/pgx/v5/pgtype"
)

type NextMatchday struct {
	Matchday  pgtype.Int4
	Season    string
	StartTime pgtype.Timestamp
}

func GetNextMatchday() (NextMatchday, error) {
	db := New()

	var nextMatchday NextMatchday
	err := db.QueryRow(
		`SELECT matchday, season, start_datetime
		FROM bavariada.matchdays
		WHERE matchday = (
			SELECT MAX(matchday)
			FROM bavariada.matchdays
			WHERE season = '2024-2025'
			AND status = 'FINISHED'
		)`,
	).Scan(&nextMatchday.Matchday, &nextMatchday.Season, &nextMatchday.StartTime)
	if err != nil {
		return NextMatchday{}, err
	}

	return nextMatchday, nil
}

func GetMatchdayInProg() (int32, error) {
	db := New()

	var maxMatchday pgtype.Int4
	err := db.QueryRow(
		`SELECT COALESCE(
			(
				SELECT MAX(matchday)
				FROM bavariada.matchdays
				WHERE season = '2024-2025'
				AND status = 'IN_PROGRESS'
			),
			(
				SELECT MAX(matchday)
				FROM bavariada.matchdays
				WHERE season = '2024-2025'
				AND status = 'NOT_STARTED'
			),
			(
				SELECT MAX(matchday)
				FROM bavariada.matchdays
				WHERE season = '2024-2025'
				AND status = 'FINISHED'
			)
		) as latest_matchday;`,
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
	defer rows.Close()

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
