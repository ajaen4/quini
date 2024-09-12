.PHONY: build run migrations setup

-include ../../.env

setup:
	@$(eval DB_STRING=postgres://$(DB_USERNAME):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/$(DB_NAME))

open-db-conn: setup
	@PGPASSWORD=$(DB_PASSWORD) psql -h $(DB_HOST) -U $(DB_USERNAME) -d $(DB_NAME)

build-local:
	@go build -o ./bin/main main.go

build:
	@CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o ./bin/main main.go

run:
	@make docs
	@air

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