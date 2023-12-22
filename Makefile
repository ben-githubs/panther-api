install-poetry:
	which poetry || python3 -m pip install poetry

fmt:
	poetry run black --line-length=100 panther_seim

lint:
	poetry run pylint panther_seim
	poetry run black --line-length=100 --check panther_seim

install:
	poetry install --without dev

install-dev:
	poetry install

test:
	poetry run pytest tests/

test-live:
	TEST_LIVE=true poetry run pytest tests/