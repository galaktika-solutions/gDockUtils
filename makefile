SHELL=/bin/bash
version := $(shell sed -rn "s/^VERSION = '(.*)'$$/\1/p" setup.py)

version:
	@echo $(version)

build:
	docker-compose build

test:
	docker-compose run --rm python bash -c "\
		coverage run --source gdockutils -m unittest && \
		coverage report && \
		coverage html \
	"

.PHONY: docs
docs:
	docker-compose run --rm python sphinx-build -b html docs/source docs/build

distribute: build test docs
	docker-compose run --rm python bash -c "\
		rm -rf dist && \
		python setup.py sdist && \
		twine upload dist/* \
	"
	git tag $(version)
	git push --tags

bash:
	docker-compose run --rm python bash
