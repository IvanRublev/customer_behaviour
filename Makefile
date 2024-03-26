.PHONY: deps lint shell migration migrate_current migrate_up migrate_down server server_headless test postgres_up postgres_down docker_up docker_down

deps:
	poetry install
	./clone_github_deps.sh

lint:
	poetry run ruff check . 

shell:
	poetry run python

server:
	poetry run python prepare_data.py && poetry run streamlit run app.py

server_headless:
	poetry run python prepare_data.py && poetry run streamlit run app.py --browser.serverAddress 0.0.0.0 --server.headless true

migration:
	if [ -z "$(m)" ]; then echo "Migration message is required. Use: make migration m='your message'"; exit 1; fi
	poetry run alembic revision -m "$(m)"

migrate_current:
	poetry run alembic current

migrate_up:
	poetry run alembic upgrade head

migrate_down:
	poetry run alembic downgrade -1

test:
	export DATABASE_URL=$${DATABASE_URL}_test; \
	poetry run alembic upgrade head; \
	poetry run -- ptw -- -s -vv $(args)

test_once:
	export DATABASE_URL=$${DATABASE_URL}_test; \
	poetry run alembic upgrade head; \
	poetry run pytest -s

postgres_up:
	docker-compose -f docker-compose-postgres.yml up -d

postgres_down:
	docker-compose -f docker-compose-postgres.yml down

docker_up:
	docker build -t customer-behaviour . && docker run -d -e STREAMLIT_SERVER_COOKIE_SECRET=$${STREAMLIT_SERVER_COOKIE_SECRET} -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/customer_trends_dev -e STREAMLIT_SERVER_PORT=$${STREAMLIT_SERVER_PORT} -p $${STREAMLIT_SERVER_PORT}:$${STREAMLIT_SERVER_PORT} customer-behaviour

docker_down:
	docker ps -a -q --filter ancestor=customer-behaviour | xargs -I {} sh -c 'docker stop {} && docker rm {}'