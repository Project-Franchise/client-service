PYTHON = python

.DEFAULT_GOAL = help

help:
	@echo -----------------------------------     Makefile for Flask app     ---------------------------
	@echo USAGE:
	@echo 	make dependencies		Install all project dependencies
	@echo 	make docker-py			Run Docker with Python(Runs Python, Redis, Postgres)
	@echo		make docker			Run Docker (Runs Redis, Postgres)
	@echo		make rm-docker			Stop Docker Container/s
	@echo		make run			Run Flask app
	@echo		make test			Run tests for app
	@echo ----------------------------------------------------------------------------------------------

dependencies:
	@pip install -r requirements.txt
	@pip install -r dev-requirements.txt

docker-py:
	@docker-compose --profile dev-python up

docker:
	@docker compose --profile dev up

rm-docker:
	@docker-compose down

run:
	${PYTHON} app.py

test:
	@docker-compose --profile test up -d
	@timeout 2
	@${PYTHON} -m pytest tests/test_client_api.py
	@docker-compose down
