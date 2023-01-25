.ONESHELL:

.PHONY: week1 week2 download delete index

export FLASK_ENV := development
export WEEK1 := week1
export WEEK2 := week2

SHELL:=/bin/bash
VENV_DIR=$(shell pyenv root)/versions/search_fundamentals
PYTHON=${VENV_DIR}/bin/python

week1: 
	@eval "$$(pyenv init -)" && \
	FLASK_ENV=$(FLASK_ENV) FLASK_APP=$(WEEK1) $(PYTHON) -m flask run --port 3000 

week2: 
	@eval "$$(pyenv init -)" && \
	FLASK_ENV=$(FLASK_ENV) FLASK_APP=$(WEEK2) $(PYTHON) -m flask run --port 3000 

index: 
	./index-data.sh

delete:
	./delete-indexes.sh
	
download: 
	./download-data.sh