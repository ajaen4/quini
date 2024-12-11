package server

import (
	"net/http"
	"strconv"

	"app/internal/db"
	"app/internal/responses"
)

type ChartData struct {
	Categories     []string `json:"categories"`
	Series         []Series `json:"series"`
	TotalMatchdays int32    `json:"total_matchdays"`
}

type Series struct {
	UserName         string `json:"user_name"`
	CumulativePoints []int  `json:"cumulative_points"`
	Color            string `json:"color"`
}

func (s *Server) GraphContents(w http.ResponseWriter, r *http.Request) error {
	userPoints, err := db.GetUserPoints()

	if err != nil {
		return err
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

	categories, err := db.GetMatchdays()
	if err != nil {
		return err
	}
	categoriesStr := []string{}
	for _, category := range categories {
		categoriesStr = append(categoriesStr, strconv.Itoa(category))
	}

	totalMatchdays, err := db.TotalMatchdays()
	if err != nil {
		return err
	}

	responses.RespondWithJSON(w, http.StatusOK, ChartData{
		Categories:     categoriesStr,
		Series:         series,
		TotalMatchdays: totalMatchdays,
	})
	return nil
}
