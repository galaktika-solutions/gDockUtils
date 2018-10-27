SHELL=/bin/bash
version := $(shell sed -rn "s/^VERSION = '(.*)'$$/\1/p" setup.py)

version:
	@echo $(version)

build:
	docker-compose build

test:
	docker-compose run --rm postgres bash -c "\
		coverage run --source gdockutils -m unittest && \
		coverage report && \
		coverage html \
	"

.PHONY: docs
docs:
	docker-compose run --rm postgres sphinx-build -b html docs/source docs/build

distribute: build test docs
	docker-compose run --rm postgres distribute
	git tag $(version)
	git push --tags

bash:
	docker-compose run --rm postgres bash
