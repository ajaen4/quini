package server

import (
	"errors"
	"fmt"
	"log"
	"slices"
	"strconv"

	"net/http"
	"net/url"

	"app/internal/components/shared/messages"
	"app/internal/db"
)

type Prediction struct {
	Cols     []string `json:"cols"`
	IsElige8 bool     `json:"isElige8"`
}

func (s *Server) NewPrediction(w http.ResponseWriter, r *http.Request) error {
	if err := r.ParseForm(); err != nil {
		return errors.New("Error parsing form")
	}

	userId := r.Context().Value("userId").(string)
	_, err := db.GetBalance(userId)
	if err != nil {
		return Render(w, r, messages.PopUp(false, "Dinero insuficiente en cuenta", false))
	}

	if isValid, errMess := isValidPreds(r.Form); !isValid {
		return Render(w, r, messages.PopUp(false, errMess, false))
	}

	predictions, err := formToPredictions(userId, r.Form)
	if err != nil {
		return err
	}

	log.Print(predictions)
	err = db.UpdateBalance(userId, -2.5)
	if err != nil {
		return err
	}

	return Render(w, r, messages.PopUp(true, "Quiniela cargada con éxito!", true))
}

func isValidPreds(preds url.Values) (bool, string) {

	if _, ok := preds["season"]; !ok {
		return false, "Falta la temporada"
	}

	if _, ok := preds["matchday"]; !ok {
		return false, "Falta la jornada"
	}

	elige8Count := 0
	allowedPred := []string{"1", "X", "2"}
	for i := 0; i < 14; i++ {
		for col := 0; col < 1; col++ {
			if value, ok := preds[fmt.Sprintf("match_num_%d_col_%d", i, col)]; !ok || !slices.Contains(allowedPred, value[0]) {
				return false, fmt.Sprintf("Valor para el partido %d y columna %d no valido", i+1, col+1)
			}
		}

		if elige8, ok := preds[fmt.Sprintf("match_num_%d_elige8", i)]; ok && elige8[0] == "on" {
			elige8Count++
		}
	}

	if elige8Count != 8 {
		return false, fmt.Sprintf("Faltan partidos para el elige8, hay %d y se necesitan 8", elige8Count)
	}

	allowedPleno := []string{"0", "1", "2", "M"}
	if plenoHome, ok := preds["pleno_home_score"]; !ok || !slices.Contains(allowedPleno, plenoHome[0]) {
		return false, fmt.Sprintf("Falta la predicción para el local en el Pleno al 15")
	}
	if plenoAway, ok := preds["pleno_away_score"]; !ok || !slices.Contains(allowedPleno, plenoAway[0]) {
		return false, fmt.Sprintf("Falta la predicción para el visitante en el Pleno al 15")
	}

	return true, ""
}

type PredictionDB struct {
	UserID     string
	Season     string
	Matchday   int
	MatchNum   int
	ColNum     int
	Prediction string
	IsElige8   bool
}

func formToPredictions(userID string, form url.Values) ([]PredictionDB, error) {
	predictions := make([]PredictionDB, 0)

	matchday, err := strconv.Atoi(form["matchday"][0])
	if err != nil {
		return []PredictionDB{}, err
	}
	season := form["season"][0]

	for matchNum := 0; matchNum < 14; matchNum++ {
		for colNum := 0; colNum < 1; colNum++ {
			pred := PredictionDB{
				UserID:     userID,
				Season:     season,
				Matchday:   matchday,
				MatchNum:   matchNum,
				ColNum:     colNum,
				Prediction: form[fmt.Sprintf("match_num_%d_col_%d", matchNum, colNum)][0],
				IsElige8:   false,
			}

			if elige8, ok := form[fmt.Sprintf("match_num_%d_elige8", matchNum)]; ok && elige8[0] == "on" {
				pred.IsElige8 = true
			}

			predictions = append(predictions, pred)
		}
	}

	homeScore := form["pleno_home_score"][0]
	awayScore := form["pleno_away_score"][0]
	for col := 0; col < 2; col++ {
		pleno := PredictionDB{
			UserID:     userID,
			Season:     season,
			Matchday:   matchday,
			MatchNum:   14,
			ColNum:     col,
			Prediction: fmt.Sprintf("%s-%s", homeScore, awayScore),
			IsElige8:   false,
		}
		predictions = append(predictions, pleno)
	}

	return predictions, nil
}
