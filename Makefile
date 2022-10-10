.PHONY: help, setup, install
#.PHONY: help, setup, install, pytest, black, isort, mypy, test

# ---------------------------------------------------------------------------- #

#python_version = miniforge3-4.10.3-10
python_version = 3.9.13
python_env = corise_search_fund

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------- #
# devoloper python setup
# ---------------------------------------------------------------------------- #

setup:   ## setup python virtual environment
	pyenv install --skip-existing $(python_version) &&\
	pyenv uninstall -f $(python_env) &&\
	pyenv virtualenv --force $(python_version) $(python_env) &&\
	pyenv local $(python_env) &&\
	pip install --upgrade pip &&\
	pip install -r requirements.txt &&\
	python --version

install:   ## install/reinstall python requirements into virtual env
	pip install --upgrade pip &&\
	pip install -r requirements.txt &&\
	python --version

# ---------------------------------------------------------------------------- #
# test
# ---------------------------------------------------------------------------- #

#pytest:  ## run pytest
#	pytest $$(find ./tests -name '*.py')
#
#black:  ## test code formatting with black
#	black $$(find ./src -name '*.py') --check
#
#isort:  ## test import formatting with isort
#	isort --profile="black" $$(find ./src -name '*.py') --check-only
#
#mypy:   ## check types with mypy
#	mypy --ignore-missing-imports --show-error-codes $$(find ./src -name '*.py')
#
#test: black isort mypy pytest  ## run all tests
