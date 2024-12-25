package server

import (
	"app/internal/responses"
	"net/http"

	"github.com/stripe/stripe-go/v81"
	"github.com/stripe/stripe-go/v81/checkout/session"
)

func (s *Server) createCheckoutSession(w http.ResponseWriter, r *http.Request) error {
	stripe.Key = s.stripeSecKey

	params := &stripe.CheckoutSessionParams{
		UIMode:    stripe.String("embedded"),
		ReturnURL: stripe.String("/checkout/return?session_id={CHECKOUT_SESSION_ID}"),
		LineItems: []*stripe.CheckoutSessionLineItemParams{
			&stripe.CheckoutSessionLineItemParams{
				// Provide the exact Price ID (for example, pr_1234) of the product you want to sell
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
