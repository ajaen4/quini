.PHONY: setup build-local build templ notify-templ-proxy run tailwindcss

-include ../../.env

setup:
	@$(eval DB_STRING=postgres://$(DB_USERNAME):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/$(DB_NAME))

build-local:
	@go build -tags local -o ./bin/main cmd/main/main.go

build:
	@CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o ./bin/main .

templ:
	@templ generate --watch --proxy=http://localhost:$(APP_PORT) --proxyport=$(TEMPL_PROXY_PORT) --open-browser=false --proxybind="0.0.0.0"

notify-templ-proxy:
	@templ generate --notify-proxy --proxyport=$(TEMPL_PROXY_PORT) 

run:
	@make templ & sleep 2
	@make tailwind &
	@air 

tailwind:
	@npm run watch

open-db-conn: setup
	@PGPASSWORD=$(DB_PASSWORD) psql -h $(DB_HOST) -U $(DB_USERNAME) -d $(DB_NAME)

create-migration: setup
	@if [ -z "$(MIGRATION_NAME)" ]; then \
		echo "Error: MIGRATION_NAME is not set"; \
		exit 1; \
	fi
	@echo "Creating migration: $(MIGRATION_NAME)"
	@goose -dir $(MIGRATION_DIR) create $(MIGRATION_NAME) sql

# GOOSE_DBSTRING must have "" around it so the make file interprets correctly certain special characters
run-migrations: setup
	@goose -dir $(MIGRATION_DIR) $(DB_DRIVER) "$(DB_STRING)" up

reset-migrations: setup
	@goose -dir $(MIGRATION_DIR) $(DB_DRIVER) "$(DB_STRING)" reset

migrations-status: setup
	@goose -dir $(MIGRATION_DIR) $(DB_DRIVER) "$(DB_STRING)" status