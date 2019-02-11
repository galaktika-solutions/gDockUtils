SHELL=/bin/bash
version := $(shell sed -rn "s/^VERSION = \"(.*)\"$$/\1/p" setup.py)

init:
	docker-compose run --rm -u "$$(id -u):$$(id -g)" main bash -c ' \
		set -e; \
		python3.6 -m venv ./.venv; \
		pip install --upgrade pip; \
		pip install -e .[dev] \
	'

build:
	docker-compose build

version:
	@echo $(version)

test:
	docker-compose run --rm main bash -c ' \
		set -e; \
		coverage run -m unittest; \
		coverage report \
	'
	docker-compose run --rm -u "$$(id -u):$$(id -g)" main coverage html
	docker-compose run --rm main find . -type d -name __pycache__ -exec rm -rf {} +

.PHONY: docs
docs:
	docker-compose run --rm -e "VERSION=$(version)" -u "$$(id -u):$$(id -g)" \
		main sphinx-build -b html docs/source docs/build

distribute: build test docs
	docker-compose run --rm main bash -c ' \
		set -e; \
		rm -rf dist; \
		python setup.py sdist; \
		TWINE_USERNAME="$$(gstack conf get PYPI_USERNAME)" \
		TWINE_PASSWORD="$$(gstack conf get PYPI_PASSWORD)" \
			twine upload dist/* \
	'
	git tag $(version)
	git push --tags
