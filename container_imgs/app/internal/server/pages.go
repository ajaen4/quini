package server

import (
	"app/internal/components/pages"
	"errors"
	"fmt"

	"net/http"

	"github.com/stripe/stripe-go/v81"
	"github.com/stripe/stripe-go/v81/checkout/session"
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
	sessionID := r.URL.Query().Get("session_id")
	if sessionID == "" {
		return errors.New("no session ID provided")
	}

	stripe.Key = s.stripeSecKey
	params := &stripe.CheckoutSessionParams{}
	session, err := session.Get(sessionID, params)
	if err != nil {
		return fmt.Errorf("Error checking session status %w", err)
	}
	if session == nil {
		return errors.New("Session not found")
	}

	switch session.Status {
	case "open":
		http.Redirect(w, r, "/checkout", http.StatusSeeOther)
		return nil
	case "complete":
		return Render(w, r, pages.ReturnCheckout(s.postHogKey, session.CustomerDetails.Email))
	default:
		return errors.New("Invalid session status")
	}
}
