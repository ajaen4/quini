package server

import (
	"app/internal/components/pages"

	"net/http"
	"os"
)

func (s *Server) Root(w http.ResponseWriter, r *http.Request) error {
	return Render(w, r, pages.Home(os.Getenv("POSTHOG_KEY")))
}

func (s *Server) Login(w http.ResponseWriter, r *http.Request) error {
	return Render(w, r, pages.Login(os.Getenv("POSTHOG_KEY"), os.Getenv("GOOGLE_CLIENT_ID")))
}
