//go:build local
// +build local

package env

import (
	"log"

	"github.com/joho/godotenv"
)

func init() {
	if err := godotenv.Load("../../.env"); err != nil {
		log.Fatal(err)
	}
}
