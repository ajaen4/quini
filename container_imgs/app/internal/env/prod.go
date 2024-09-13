//go:build !local
// +build !local

package env

import (
	"log"
)

func init() {
	log.Print("Running prod mode")
}
