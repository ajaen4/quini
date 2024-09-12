package server

import (
	"app/internal/components"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

func (api *Api) RegisterRoutes() *chi.Mux {
	r := chi.NewRouter()

	r.Use(middleware.Heartbeat("/ping"))
	r.Use(middleware.Logger)

	r.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		components.Hello("a").Render(r.Context(), w)
	})

	return r
}
