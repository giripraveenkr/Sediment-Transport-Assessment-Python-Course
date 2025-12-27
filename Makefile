.PHONY: all data build test lint fmt clean

all: data build test

data:
	python -m src.wrr.scripts.prepare_data

build:
	python -m src.wrr.scripts.run_analysis

test:
	pytest -m "not heavy"

lint:
	ruff check . && black --check .

fmt:
	black . && ruff check --fix .

clean:
	rm -rf results/* figures/* || true
