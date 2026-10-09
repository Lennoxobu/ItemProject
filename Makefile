.PHONY: start stop down logs

start:
	docker compose up -d
	@echo "Waiting for postgres to be ready..."
	@until docker compose exec -T db pg_isready -U itemproject -d itemproject >/dev/null 2>&1; do sleep 1; done
	@echo "Postgres is ready on localhost:5432"

stop:
	docker compose stop

down:
	docker compose down -v

logs:
	docker compose logs -f db
