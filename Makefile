
.PHONY: run-dev run-prod
run-dev:
	COMPOSE_PROFILES=dev docker compose --env-file .env.dev up --build

run-prod:
	COMPOSE_PROFILES=prod docker compose --env-file .env.prod up --build
