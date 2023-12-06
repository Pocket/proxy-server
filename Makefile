.PHONY: build
build:
	docker compose build

.PHONY: start
start:
	docker compose up

.PHONY: destroy
destroy:
	docker compose down --rmi all --remove-orphans -v
