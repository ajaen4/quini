package server

import (
	"aws_lib/aws_lib"
	"encoding/gob"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/gorilla/sessions"
)

type Server struct {
	httpServer *http.Server
	router     chi.Router
	store      *sessions.CookieStore
	projectURL string
	anonKey    string
}

func NewServer(port int) *Server {

	// Register time.Time with Go's encoding/gob to allow storing timestamps in sessions.
	// This is required because gorilla/sessions uses gob to serialize session data.
	gob.Register(time.Time{})

	env := os.Getenv("ENV")

	if env != "LOCAL" {
		sm := aws_lib.NewSSM("")
		param := sm.GetParam(fmt.Sprintf("/quini/secrets/%s", env), true)
		for varName, varValue := range param {
			if err := os.Setenv(varName, varValue); err != nil {
				log.Fatal("failed to set environment variable %s: %w", varName, err)
			}
		}
	}

	key := []byte(os.Getenv("SESSION_KEY"))
	isSecure := env != "LOCAL"

	store := sessions.NewCookieStore(key)
	store.Options = &sessions.Options{
		Path:     "/",
		MaxAge:   86400 * 7,
		HttpOnly: true,
		Secure:   isSecure,
		SameSite: http.SameSiteLaxMode,
	}

	r := chi.NewRouter()

	r.Use(middleware.Heartbeat("/ping"))
	r.Use(middleware.Logger)

	httpServer := &http.Server{
		Addr:         fmt.Sprintf(":%d", port),
		Handler:      r,
		IdleTimeout:  time.Minute,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 30 * time.Second,
	}

	server := &Server{
		store:      store,
		projectURL: os.Getenv("SUPABASE_URL"),
		anonKey:    os.Getenv("SUPABASE_KEY"),
		httpServer: httpServer,
		router:     r,
	}

	server.RegisterRoutes()

	return server
}

func (server *Server) Start() error {
	return server.httpServer.ListenAndServe()
}

func (server *Server) Close() error {
	return server.httpServer.Close()
}
