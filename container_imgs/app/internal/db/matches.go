package db

import (
	"github.com/jackc/pgx/v5/pgtype"
)

type Match struct {
	Status          string           `json:"status"`
	MatchNum        int              `json:"match_num"`
	HomeCode        string           `json:"home_code"`
	HomeName        string           `json:"home_name"`
	HomeLogo        string           `json:"home_logo_url"`
	HomeGoals       pgtype.Int4      `json:"home_goals"`
	AwayCode        string           `json:"away_code"`
	AwayName        string           `json:"away_name"`
	AwayLogo        string           `json:"away_logo_url"`
	AwayGoals       pgtype.Int4      `json:"away_goals"`
	KickoffDatetime pgtype.Timestamp `json:"kickoff_datetime"`
	Minutes         pgtype.Int4      `json:"minutes"`
	HomePercent     pgtype.Int4      `json:"home_percent"`
	DrawPercent     pgtype.Int4      `json:"draw_percent"`
	AwayPercent     pgtype.Int4      `json:"away_percent"`
}

func GetMatches(matchday int32) ([]Match, error) {
	db := New()

	rows, err := db.Query(
		`SELECT
			status,
			matches.match_num,
			home.code as home_code,
			home.name as home_name,
			home.logo_url as home_logo_url,
			home_goals,
			away.code as away_code,
			away.name as away_name,
			away.logo_url as away_logo_url,
			away_goals,
			kickoff_datetime,
			minutes,
			stats.home_percent,
			stats.draw_percent,
			stats.away_percent
		FROM bavariada.matches as matches
		LEFT JOIN bavariada.teams home ON matches.home_team_id = home.id
		LEFT JOIN bavariada.teams away ON matches.away_team_id = away.id
		LEFT JOIN bavariada.predictions_stats stats ON
			matches.season = stats.season
			AND matches.matchday = stats.matchday
			AND matches.match_num = stats.match_num
		WHERE matches.matchday = $1
		ORDER BY matches.match_num;`,
		matchday,
	)
	if err != nil {
		return []Match{}, err
	}
	defer rows.Close()

	matches := []Match{}
	for rows.Next() {
		match := Match{}
		err = rows.Scan(
			&match.Status,
			&match.MatchNum,
			&match.HomeCode,
			&match.HomeName,
			&match.HomeLogo,
			&match.HomeGoals,
			&match.AwayCode,
			&match.AwayName,
			&match.AwayLogo,
			&match.AwayGoals,
			&match.KickoffDatetime,
			&match.Minutes,
			&match.HomePercent,
			&match.DrawPercent,
			&match.AwayPercent,
		)
		if err != nil {
			return []Match{}, err
		}
		matches = append(matches, match)
	}
	return matches, nil
}
