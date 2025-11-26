SHELL := /bin/sh

DOCKER_COMPOSE := $(shell if docker compose version >/dev/null 2>&1; then echo "docker compose"; elif command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo ""; fi)
COMPOSE_FILE ?= docker-compose.yml
SERVICE ?= app

ifeq ($(strip $(DOCKER_COMPOSE)),)
$(error docker Compose is required (install 'docker compose' or 'docker-compose'))
endif

COMPOSE := $(DOCKER_COMPOSE) -f $(COMPOSE_FILE)

DEPLOY_HOST ?=
DEPLOY_USER ?= deploy
DEPLOY_PATH ?=
DEPLOY_PASSWORD ?=

SSH_PREFIX := $(if $(strip $(DEPLOY_PASSWORD)),sshpass -p "$(DEPLOY_PASSWORD)" ,)
SSH := $(SSH_PREFIX)ssh -o StrictHostKeyChecking=no $(DEPLOY_USER)@$(DEPLOY_HOST)


.PHONY: help build up down run logs ps shell test clean deploy

help: ## List available targets
	@echo "Available targets:"; \
	grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk -F ':.*?## ' '{printf "  %-12s %s\n", $$1, $$2}'

build: ## Build the Docker images
	$(COMPOSE) build

up: ## Start the stack in attached mode
	$(COMPOSE) up 

down: ## Stop and remove containers, networks, and volumes
	$(COMPOSE) down 

run: build ## Run the app service once with published ports
	$(COMPOSE) run --rm --service-ports $(SERVICE)

logs: ## Tail logs from the app service
	$(COMPOSE) logs -f $(SERVICE)

ps: ## Show compose service status
	$(COMPOSE) ps

shell: ## Start a shell inside the app service container
	$(COMPOSE) run --rm $(SERVICE) /bin/sh

test: build ## Execute pytest inside the app container
	$(COMPOSE) run --rm $(SERVICE) pytest

clean: ## Remove dangling images left by compose
	docker image prune -f

deploy: ## Deploy the stack to the remote host via SSH (requires DEPLOY_HOST and DEPLOY_PATH)
	@$(if $(strip $(DEPLOY_HOST)),,$(error DEPLOY_HOST is required))
	@$(if $(strip $(DEPLOY_PATH)),,$(error DEPLOY_PATH is required))
	$(SSH) "cd $(DEPLOY_PATH) && git pull --ff-only && $(COMPOSE) pull && $(COMPOSE) up -d --remove-orphans"
