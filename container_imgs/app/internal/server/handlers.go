package server

import (
	"app/internal/components/pages"
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
	Name  string `json:"name"`
	Data  []int  `json:"data"`
	Color string `json:"color"`
}

func graphContents(w http.ResponseWriter, r *http.Request) error {
	userPoints, err := db.GetUserPoints()
	if err != nil {
		return err
	}

	categories := make([]string, len(userPoints[0].PointsArray))
	for i := range categories {
		categories[i] = strconv.Itoa(i + 1)
	}
	series := []Series{}
	colors := []string{"#1A56DB", "#7E3AF2", "#047857", "#DC2626"}
	for i, userPoint := range userPoints {
		series = append(series, Series{
			Name:  userPoint.UserId,
			Data:  userPoint.PointsArray,
			Color: colors[i],
		})
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(ChartData{
		Categories: categories,
		Series:     series,
	})
	return nil
}

func root(w http.ResponseWriter, r *http.Request) error {
	return Render(w, r, pages.Home())
}
