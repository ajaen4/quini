package server

import (
	"app/internal/components/pages"
	"app/internal/components/shared/badges"
	"app/internal/components/shared/messages"
	"app/internal/components/shared/tables"
	"app/internal/db"
	"net/http"
	"strconv"
)

type ChartData struct {
	Categories []string `json:"categories"`
	Series     []Series `json:"series"`
}

type Series struct {
	UserName         string `json:"user_name"`
	CumulativePoints []int  `json:"cumulative_points"`
	Color            string `json:"color"`
}

func graphContents(w http.ResponseWriter, r *http.Request) error {
	userPoints, err := db.GetUserPoints()
	if err != nil {
		return err
	}

	categories := make([]string, len(userPoints[0].CumulativePoints))
	for i := range categories {
		categories[i] = strconv.Itoa(i + 1)
	}
	series := []Series{}
	usersColor := map[string]string{
		"Jaen":   "#1A56DB",
		"Silvan": "#7E3AF2",
		"Barja":  "#047857",
		"Dordio": "#DC2626",
		"Alber":  "#F97316",
	}
	for _, userPoint := range userPoints {
		series = append(series, Series{
			UserName:         userPoint.UserName,
			CumulativePoints: userPoint.CumulativePoints,
			Color:            usersColor[userPoint.UserName],
		})
	}

	respondWithJSON(w, http.StatusOK, ChartData{
		Categories: categories,
		Series:     series,
	})
	return nil
}

func totalResults(w http.ResponseWriter, r *http.Request) error {
	userResults, err := db.GetTotalResults()
	if err != nil {
		return err
	}

	return Render(w, r, tables.TotalResults(userResults))
}

func totalDebt(w http.ResponseWriter, r *http.Request) error {
	totalDebt, err := db.GetTotalDebt()
	if err != nil {
		return err
	}

	return Render(w, r, badges.TotalMetric("Bote", totalDebt))
}

func totalPrice(w http.ResponseWriter, r *http.Request) error {
	totalPrice, err := db.GetTotalPrice()
	if err != nil {
		return err
	}

	return Render(w, r, badges.TotalMetric("Premios", totalPrice))
}

func resultsPerMatchday(w http.ResponseWriter, r *http.Request) error {
	resultsPerMatchday, err := db.GetResultsPerMatchday()
	if err != nil {
		return err
	}

	return Render(w, r, tables.ResultsPerMatchday(resultsPerMatchday))
}

func matchdayPredictions(w http.ResponseWriter, r *http.Request) error {
	maxMatchday, err := db.GetMatchdayInProg()
	if err != nil {
		return err
	}
	if maxMatchday == 0 {
		return Render(w, r, messages.Message("Ninguna jornada en progreso"))
	}

	matchdayPredictions, err := db.GetUserPredictions(maxMatchday)
	if err != nil {
		return err
	}

	matches, err := db.GetMatches(maxMatchday)
	if err != nil {
		return err
	}

	return Render(w, r, tables.MatchdayPredictions(matches, matchdayPredictions))
}

func root(w http.ResponseWriter, r *http.Request) error {
	return Render(w, r, pages.Home())
}
