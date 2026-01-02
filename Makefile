.PHONY: install test run

install:
	pip install -r requirements.txt

test:
	python -m unittest discover -v

run:
	python main.py
