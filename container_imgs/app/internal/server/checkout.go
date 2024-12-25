package server

import (
	"app/internal/responses"
	"fmt"
	"net/http"

	"github.com/stripe/stripe-go/v81"
	"github.com/stripe/stripe-go/v81/checkout/session"
)

func (s *Server) createCheckoutSession(w http.ResponseWriter, r *http.Request) error {
	stripe.Key = s.stripeSecKey

	var returnUrls = map[string]string{
		"LOCAL": "http://localhost:8081",
		"dev":   "https://dev.quini.io",
		"prod":  "https://quini.io",
	}

	returnUrl, ok := returnUrls[s.env]
	if !ok {
		return fmt.Errorf("invalid environment: %s", s.env)
	}

	params := &stripe.CheckoutSessionParams{
		UIMode:    stripe.String("embedded"),
		ReturnURL: stripe.String(fmt.Sprintf("%s/checkout/return?session_id={CHECKOUT_SESSION_ID}", returnUrl)),
		LineItems: []*stripe.CheckoutSessionLineItemParams{
			&stripe.CheckoutSessionLineItemParams{
				Price:    stripe.String("price_1QYuWzG7LJ1N13dOcJH7xmsi"),
				Quantity: stripe.Int64(1),
			},
		},
		Mode: stripe.String(string(stripe.CheckoutSessionModePayment)),
	}

	session, err := session.New(params)

	if err != nil {
		return err
	}

	responses.RespondWithJSON(w, http.StatusOK, struct {
		ClientSecret string `json:"clientSecret"`
	}{
		ClientSecret: session.ClientSecret,
	})

	return nil
}

func (s *Server) retrieveCheckoutSession(w http.ResponseWriter, r *http.Request) error {
	session, _ := session.Get(r.URL.Query().Get("session_id"), nil)

	responses.RespondWithJSON(w, http.StatusOK, struct {
		Status        string `json:"status"`
		CustomerEmail string `json:"customer_email"`
	}{
		Status:        string(session.Status),
		CustomerEmail: string(session.CustomerDetails.Email),
	})

	return nil
}
