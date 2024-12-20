package server

import (
	"app/internal/db"
	"app/internal/responses"
	"net/http"
)

func (s *Server) Health(w http.ResponseWriter, r *http.Request) error {
	health := db.New().Health()
	responses.RespondWithJSON(w, 200, health)
	return nil
}
