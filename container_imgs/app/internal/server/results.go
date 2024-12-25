package server

import (
	"app/internal/components/shared/badges"
	"app/internal/components/shared/forms"
	"app/internal/components/shared/messages"
	"app/internal/components/shared/tables"
	"app/internal/db"

	"net/http"
	"sort"
)

func (s *Server) TotalResults(w http.ResponseWriter, r *http.Request) error {
	userResults, err := db.GetTotalResults()
	if err != nil {
		return err
	}

	return Render(w, r, tables.TotalResults(userResults))
}

func (s *Server) TotalDebt(w http.ResponseWriter, r *http.Request) error {
	totalDebt, err := db.GetTotalDebt()
	if err != nil {
		return err
	}

	return Render(w, r, badges.TotalMetric("Bote", totalDebt))
}

func (s *Server) TotalPrice(w http.ResponseWriter, r *http.Request) error {
	totalPrice, err := db.GetTotalPrice()
	if err != nil {
		return err
	}

	return Render(w, r, badges.TotalMetric("Premios", totalPrice))
}

func (s *Server) ResultsPerMatchday(w http.ResponseWriter, r *http.Request) error {
	resultsPerMatchday, err := db.GetResultsPerMatchday()
	if err != nil {
		return err
	}

	return Render(w, r, tables.ResultsPerMatchday(resultsPerMatchday))
}

func (s *Server) MatchdayPredictions(w http.ResponseWriter, r *http.Request) error {
	matchdayInProg, err := db.GetMatchdayInProg()
	if err != nil {
		return err
	}
	if matchdayInProg == 0 {
		return Render(w, r, messages.Message("Ninguna jornada en progreso"))
	}

	matchdayPredictions, err := db.GetUserPredictions(matchdayInProg)
	if err != nil {
		return err
	}

	users, err := db.GetUsers()
	if err != nil {
		return err
	}

	for userId, userName := range users {
		if _, ok := matchdayPredictions[userId]; !ok {
			matchdayPredictions[userId] = db.UserPredictions{
				UserName: userName,
			}
		}
	}

	values := []db.UserPredictions{}
	for _, v := range matchdayPredictions {
		values = append(values, v)
	}

	sort.Slice(values, func(i, j int) bool {
		return values[i].UserName < values[j].UserName
	})

	matches, err := db.GetMatches(matchdayInProg)
	if err != nil {
		return err
	}

	return Render(w, r, tables.MatchdayPredictions(matches, values))
}

func (s *Server) NextMatchday(w http.ResponseWriter, r *http.Request) error {
	nextMatchday, err := db.GetNextMatchday()
	if err != nil {
		return Render(w, r, messages.Message("Próxima jornada no registrada"))
	}

	userId := r.Context().Value("userId").(string)
	userLastMatchday, err := db.GetUserLastMatchday(userId)
	if err != nil {
		return err
	}

	matchdayNum := nextMatchday.Matchday.Int32
	if userLastMatchday == matchdayNum {
		return Render(w, r, messages.Message("Próxima jornada no registrada"))
	}

	matches, err := db.GetMatches(matchdayNum)
	if err != nil {
		return err
	}

	balance, err := db.GetBalance(userId)
	if err != nil {
		return err
	}

	return Render(w, r, forms.PredictionsForm(nextMatchday, matches, balance))
}
