.PHONY: check install develop test lint flake retest

check:
	python setup.py check

install:
	python setup install

develop:
	python setup develop

lint:
	black .
	isort -y
	flake8 .

pre:
	pre-commit run -a

flake:
	flake8 .

test:
	pytest -v  . --cov=msalign --cov-report=html --cov-report term

retest:
	pytest -v . --lf

docs:
	activate mkdocs
	mkdocs serve
