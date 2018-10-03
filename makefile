version := $(shell sed -rn "s/^VERSION = '(.*)'$$/\1/p" setup.py)

version:
	@echo $(version)

build:
	docker-compose build

install:
	docker-compose run --rm python install

test:
	docker-compose run --rm python test

.PHONY: docs
docs:
	docker-compose run --rm python docs

distribute: build install test docs
	docker-compose run --rm python sdist
	docker-compose run --rm python twine upload dist/*
	git tag $(version)
	git push --tags

bash:
	docker-compose run --rm python bash
