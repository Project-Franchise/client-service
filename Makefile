PYTHON = python

.DEFAULT_GOAL = help

help:
	@echo ------------------------------Makefile for Flask app------------------------------
	@echo USAGE:
	@echo 	make dependencies			Install all project dependencies
	@echo 		make docker-not-dev		Run Docker with Python
	@echo		make docker				Run Docker
	@echo		make rm-docker				Stop Docker Container/s
	@echo		make run				Run Flask app
	@echo		make test				Run tests for app
	@echo ----------------------------------------------------------------------------------

dependencies:
	@pip install -r requirements.txt
	@pip install -r dev-requirements.txt

docker:
	@docker compose up -d

docker-not-dev:
	@docker compose --profile not-dev up

rm-docker:
	@docker compose down

run:
	${PYTHON} app.py

test:
	@docker compose -f docker-test.yaml up -d
	@${PYTHON} -m pytest tests/test.py
	@docker compose down
