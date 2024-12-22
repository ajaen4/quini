package server

import (
	"app/internal/responses"
	"net/http"

	"github.com/stripe/stripe-go/v81"
	"github.com/stripe/stripe-go/v81/checkout/session"
)

func createCheckoutSession(w http.ResponseWriter, r *http.Request) error {
	stripe.Key = "sk_test_51QYu2rG7LJ1N13dOmZwL3Ybv0lp6Hr8neWWX7RFqD2HXAVnK7BmuZmWIPcHlSAoIulD0lfpFCyXylGQAaiMz0HIA00rZgbwa7d"

	domain := "http://localhost:8081"
	params := &stripe.CheckoutSessionParams{
		UIMode:    stripe.String("embedded"),
		ReturnURL: stripe.String(domain + "/checkout/return?session_id={CHECKOUT_SESSION_ID}"),
		LineItems: []*stripe.CheckoutSessionLineItemParams{
			&stripe.CheckoutSessionLineItemParams{
				// Provide the exact Price ID (for example, pr_1234) of the product you want to sell
				Price:    stripe.String("price_1QYuWzG7LJ1N13dOcJH7xmsi"),
				Quantity: stripe.Int64(1),
			},
		},
		Mode: stripe.String(string(stripe.CheckoutSessionModePayment)),
	}

	s, err := session.New(params)

	if err != nil {
		return err
	}

	responses.RespondWithJSON(w, http.StatusOK, struct {
		ClientSecret string `json:"clientSecret"`
	}{
		ClientSecret: s.ClientSecret,
	})

	return nil
}

func retrieveCheckoutSession(w http.ResponseWriter, r *http.Request) error {
	s, _ := session.Get(r.URL.Query().Get("session_id"), nil)

	responses.RespondWithJSON(w, http.StatusOK, struct {
		Status        string `json:"status"`
		CustomerEmail string `json:"customer_email"`
	}{
		Status:        string(s.Status),
		CustomerEmail: string(s.CustomerDetails.Email),
	})

	return nil
}
