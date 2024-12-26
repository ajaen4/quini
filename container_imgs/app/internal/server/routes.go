package server

import (
	"log"
	"net/http"

	"app/internal"
	"app/internal/api_errors"
	"app/internal/responses"

	"github.com/go-chi/chi/v5"
)

func (server *Server) RegisterRoutes() {

	server.router.Handle("/static/*", http.FileServer(http.FS(internal.StaticFiles)))
	server.router.Get("/health", NewHandler(server.Health))

	server.router.Post("/auth/google", NewHandler(server.HandleGoogleAuth))
	server.router.Get("/auth/logout", NewHandler(server.HandleLogout))
	server.router.Get("/login", NewHandler(server.Login))
	server.router.Get("/checkout", NewHandler(server.Checkout))
	server.router.Get("/checkout/return", NewHandler(server.ReturnCheckout))

	server.router.Group(func(r chi.Router) {
		r.Use(server.AuthAPIMiddleware)

		r.Get("/points/cumulative", NewHandler(server.GraphContents))

		r.Get("/components/tables/total-points", NewHandler(server.TotalResults))
		r.Get("/components/badges/total-debt", NewHandler(server.TotalDebt))
		r.Get("/components/badges/total-price", NewHandler(server.TotalPrice))
		r.Get("/components/tables/points-per-matchday", NewHandler(server.ResultsPerMatchday))
		r.Get("/components/tables/matchday-predictions", NewHandler(server.MatchdayPredictions))
		r.Get("/components/forms/next-matchday", NewHandler(server.NextMatchday))

		r.Post("/predictions", NewHandler(server.NewPrediction))

		r.Post("/checkout/create-session", NewHandler(server.createCheckoutSession))

	})

	server.router.Group(func(r chi.Router) {
		r.Use(server.AuthPageMiddleware)

		r.Get("/", NewHandler(server.Root))
	})
}

type CustomHandler func(w http.ResponseWriter, request *http.Request) error

// Two different handlers, one for api (htmx) methods and another for the ui.
// do it with an interface? Go through handwritten notes on that.
func NewHandler(customHandler CustomHandler) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		err := customHandler(w, r)
		if err != nil {
			log.Printf("Error: %s", err.Error())
			if clientErr, ok := err.(*api_errors.ClientErr); ok {
				responses.RespondWithJSON(w, clientErr.HttpCode, clientErr)
			} else {
				responses.RespondWithJSON(w, http.StatusInternalServerError,
					api_errors.InternalErr{
						HttpCode: http.StatusInternalServerError,
						Message:  "internal server error",
					},
				)
			}
		}
	}
}
