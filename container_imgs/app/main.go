package main

import (
	"log"

	"app/internal/server"

	_ "github.com/joho/godotenv/autoload"
)

func main() {
	port := 8080
	server := server.NewServer(port)
	log.Printf("Running server on %s", server.Addr)
	if err := server.ListenAndServe(); err != nil {
		log.Fatal(err)
	}
}
