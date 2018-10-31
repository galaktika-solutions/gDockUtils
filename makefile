SHELL=/bin/bash
version := $(shell sed -rn "s/^VERSION = '(.*)'$$/\1/p" setup.py)

clean:
	docker-compose run --rm postgres find . -type d -name __pycache__ -exec rm -rf {} +

version:
	@echo $(version)

build:
	docker-compose build

test:
	-find .files -type f -exec rm {} +
	docker-compose run --rm postgres bash -c "\
		coverage run --branch --source gdockutils -m unittest && \
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
