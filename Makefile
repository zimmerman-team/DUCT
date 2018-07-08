.PHONY: build

#builds image
build:
	docker-compose build

runserver-local:
	docker-compose -f docker-compose.dev.yml up

runserver-prod:
	docker-compose -f docker-compose.prod.yml up