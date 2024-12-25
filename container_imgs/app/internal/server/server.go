package server

import (
	"context"
	"encoding/gob"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/gorilla/sessions"
)

type Server struct {
	httpServer     *http.Server
	router         chi.Router
	store          *sessions.CookieStore
	projectURL     string
	anonKey        string
	stripePubKey   string
	stripeSecKey   string
	postHogKey     string
	googleClientId string
}

func NewServer(port int) *Server {

	// Register time.Time with Go's encoding/gob to allow storing timestamps in sessions.
	// This is required because gorilla/sessions uses gob to serialize session data.
	gob.Register(time.Time{})

	env := os.Getenv("ENV")

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
		store:          store,
		projectURL:     os.Getenv("SUPABASE_URL"),
		anonKey:        os.Getenv("SUPABASE_KEY"),
		httpServer:     httpServer,
		router:         r,
		stripePubKey:   os.Getenv("STRIPE_PUB_KEY"),
		stripeSecKey:   os.Getenv("STRIPE_SEC_KEY"),
		postHogKey:     os.Getenv("POSTHOG_KEY"),
		googleClientId: os.Getenv("GOOGLE_CLIENT_ID"),
	}

	server.RegisterRoutes()

	return server
}

func (server *Server) Start() {
	serverCtx, serverStopCtx := context.WithCancel(context.Background())

	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGHUP, syscall.SIGINT, syscall.SIGTERM, syscall.SIGQUIT)

	go func() {
		<-sig
		shutdownCtx, _ := context.WithTimeout(serverCtx, 30*time.Second)

		go func() {
			<-shutdownCtx.Done()
			if shutdownCtx.Err() == context.DeadlineExceeded {
				log.Fatal("graceful shutdown timed out.. forcing exit.")
			}
		}()

		err := server.httpServer.Shutdown(shutdownCtx)
		if err != nil {
			log.Fatal(err)
		}
		serverStopCtx()
	}()

	err := server.httpServer.ListenAndServe()
	if err != nil && err != http.ErrServerClosed {
		log.Fatal(err)
	}

	<-serverCtx.Done()
}

func (server *Server) Close() error {
	return server.httpServer.Close()
}
