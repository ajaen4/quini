package server

import (
	"app/internal/components/shared/messages"
	"errors"
	"log"

	"net/http"
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

	for key, values := range r.Form {
		for _, value := range values {
			log.Printf("%s: %s\n", key, value)
		}
	}

	return Render(w, r, messages.Message("Ok"))
}
