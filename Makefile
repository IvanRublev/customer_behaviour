.PHONY: deps lint shell migration migrate_current migrate_up migrate_down server test postgres_up postgres_down docker_up docker_down

deps:
	poetry install

lint:
	poetry run ruff check . 

shell:
	poetry run python

streamlit:
	poetry run streamlit run app.py

test:
	export DATABASE_URL=$${DATABASE_URL}_test; \
	poetry run alembic upgrade head; \
	poetry run -- ptw -- -s -v

test_once:
	export DATABASE_URL=$${DATABASE_URL}_test; \
	poetry run alembic upgrade head; \
	poetry run pytest -s

postgres_up:
	docker-compose -f docker-compose-postgres.yml up -d

postgres_down:
	docker-compose -f docker-compose-postgres.yml down

docker_up:
	docker build -t customer-trends . && docker run -d -e AUTH_TOKEN=$${AUTH_TOKEN} -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/exam_depository_dev -e PORT=$${PORT} -p $${PORT}:$${PORT} customer-trends

docker_down:
	docker ps -a -q --filter ancestor=customer-trends | xargs -I {} sh -c 'docker stop {} && docker rm {}'