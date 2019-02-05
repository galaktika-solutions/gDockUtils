SHELL=/bin/bash
version := $(shell sed -rn "s/^VERSION = '(.*)'$$/\1/p" setup.py)

init:
	docker-compose run --rm -u "$$(id -u):$$(id -g)" main pipenv install

version:
	@echo $(version)

test:
	docker-compose run --rm main pipenv run coverage run -m unittest
	docker-compose run --rm -u "$$(id -u):$$(id -g)" main pipenv run coverage report
	docker-compose run --rm -u "$$(id -u):$$(id -g)" main pipenv run coverage html

.PHONY: docs
docs:
	docker-compose run --rm -u "$$(id -u):$$(id -g)" main pipenv run sphinx-build -b html docs/source docs/build

# distribute: build test docs
# 	docker-compose run --rm postgres distribute
# 	git tag $(version)
# 	git push --tags
