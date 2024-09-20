package server

import (
	"app/internal/components/pages"
	"app/internal/components/shared/tables"
	"app/internal/db"
	"encoding/json"
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

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(ChartData{
		Categories: categories,
		Series:     series,
	})
	return nil
}

func totalPoints(w http.ResponseWriter, r *http.Request) error {
	userResults, err := db.GetTotalResults()
	if err != nil {
		return err
	}

	return Render(w, r, tables.TotalResults(userResults))
}

func pointsPerMatchday(w http.ResponseWriter, r *http.Request) error {
	resultsPerMatchday, err := db.GetResultsPerMatchday()
	if err != nil {
		return err
	}

	return Render(w, r, tables.PointsPerMatchday(resultsPerMatchday))
}

func root(w http.ResponseWriter, r *http.Request) error {
	return Render(w, r, pages.Home())
}
