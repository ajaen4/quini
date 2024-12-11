package main

import (
	"aws_lib/aws_lib"
	"fmt"
	"log"
	"os"
	"strconv"

	_ "app/internal/env"
	"app/internal/server"
)

func main() {

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

	port, err := strconv.Atoi(os.Getenv("APP_PORT"))
	if err != nil {
		log.Fatal("APP_PORT env variable not set correctly")
	}

	server := server.NewServer(port)
	defer server.Close()
	if err := server.Start(); err != nil {
		log.Printf("Server forced to shutdown: %v", err)
	}
}
