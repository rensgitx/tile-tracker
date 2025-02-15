DOCKER_COMPOSE = docker-compose
DE = docker exec
PROJECT = app

dev-up:
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up -d --build

up:
	$(DOCKER_COMPOSE) up -d --build

dev-down:
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml down

down:
	$(DOCKER_COMPOSE) down --remove-orphans

migrate:
	$(DE) $(PROJECT) python project/manage.py makemigrations trackapp
	$(DE) $(PROJECT) python project/manage.py migrate trackapp

superuser:
	@echo "Attempt creating a superuser. Allow to fail if it has been created."
	$(DE) $(PROJECT) python project/manage.py createsuperuser --no-input || true

test:
	$(DE) $(PROJECT) python project/manage.py test trackapp -v=2

# Show available commands
help:
	@echo "Available commands:"
	@echo "  (dev-)up           - Build and start the project"
	@echo "  (dev-)down         - Stop the containers"
	@echo "  migrate             - Apply database migrations"
	@echo "  superuser           - Create a superuser"
