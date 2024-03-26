.PHONY: deps lint shell server server_headless test docker_up docker_down

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

test:
	poetry run -- ptw -- -s -vv $(args)

test_once:
	poetry run pytest -s

docker_up:
	docker build -t customer-behaviour . && docker run -d -e STREAMLIT_SERVER_COOKIE_SECRET=$${STREAMLIT_SERVER_COOKIE_SECRET} -e STREAMLIT_SERVER_PORT=$${STREAMLIT_SERVER_PORT} -p $${STREAMLIT_SERVER_PORT}:$${STREAMLIT_SERVER_PORT} customer-behaviour

docker_down:
	docker ps -a -q --filter ancestor=customer-behaviour | xargs -I {} sh -c 'docker stop {} && docker rm {}'