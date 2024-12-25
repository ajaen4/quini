package server

import (
	"errors"
	"fmt"
	"log"
	"slices"

	"net/http"
	"net/url"

	"app/internal/components/shared/messages"
)

type Prediction struct {
	Cols     []string `json:"cols"`
	IsElige8 bool     `json:"isElige8"`
}

func (s *Server) NewPrediction(w http.ResponseWriter, r *http.Request) error {
	log.Print(r.Context().Value("userId").(string))

	if err := r.ParseForm(); err != nil {
		return errors.New("Error parsing form")
	}

	if isValid, errMess := isValidPreds(r.Form); !isValid {
		return Render(w, r, messages.PopUp(false, errMess))
	}

	return Render(w, r, messages.PopUp(true, "Quiniela cargada con éxito!"))
}

func isValidPreds(preds url.Values) (bool, string) {

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
