OUTPUT ?= data.csv

.PHONY: sync test run

sync:
	uv sync --locked

test:
	uv run --locked python -m unittest discover -s tests -v

run:
	uv run --locked python -m wlu --output "$(OUTPUT)"
