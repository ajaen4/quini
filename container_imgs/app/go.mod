module app

go 1.23

toolchain go1.23.3

require aws_lib v0.0.0

//go:build !container
// +build !container
replace aws_lib => ../../aws_lib

require (
	github.com/a-h/templ v0.2.793
	github.com/go-chi/chi/v5 v5.0.12
	github.com/gorilla/sessions v1.4.0
	github.com/jackc/pgx/v5 v5.7.1
	github.com/joho/godotenv v1.5.1
	github.com/stripe/stripe-go/v81 v81.2.0
)

require (
	github.com/aws/aws-sdk-go v1.55.5 // indirect
	github.com/gorilla/securecookie v1.1.2 // indirect
	github.com/jackc/pgpassfile v1.0.0 // indirect
	github.com/jackc/pgservicefile v0.0.0-20240606120523-5a60cdf6a761 // indirect
	github.com/jackc/puddle/v2 v2.2.2 // indirect
	github.com/jmespath/go-jmespath v0.4.0 // indirect
	golang.org/x/crypto v0.27.0 // indirect
	golang.org/x/sync v0.8.0 // indirect
	golang.org/x/text v0.18.0 // indirect
)
