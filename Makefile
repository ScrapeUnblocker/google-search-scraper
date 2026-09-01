.PHONY: install lint format test run clean

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .

format:
	ruff format .

test:
	pytest -q

run:
	python -m google_search_scraper.cli "web scraping tools" --country us

clean:
	rm -rf build dist *.egg-info src/*.egg-info .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
