package server

import (
	"app/internal/components/pages"

	"net/http"
)

func (s *Server) Root(w http.ResponseWriter, r *http.Request) error {
	return Render(w, r, pages.Home(s.postHogKey))
}

func (s *Server) Login(w http.ResponseWriter, r *http.Request) error {
	return Render(w, r, pages.Login(s.postHogKey, s.googleClientId))
}

func (s *Server) Checkout(w http.ResponseWriter, r *http.Request) error {
	return Render(w, r, pages.Checkout(s.postHogKey, s.stripePubKey))
}

func (s *Server) ReturnCheckout(w http.ResponseWriter, r *http.Request) error {
	return Render(w, r, pages.ReturnCheckout(s.postHogKey))
}
