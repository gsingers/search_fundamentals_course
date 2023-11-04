.ONESHELL:

.PHONY: week1 week2 download delete index

export FLASK_ENV := development
export WEEK1 := week1
export WEEK2 := week2

ifneq (,$(wildcard ./.env))
    include .env
    export
endif

SHELL:=/bin/bash

ifndef PYTHON_BIN
PYTHON_BIN=$(shell pyenv root)/versions/search_fundamentals/bin/python
endif

week1: 
	@eval "$$(pyenv init -)" && \
	FLASK_ENV=$(FLASK_ENV) FLASK_APP=$(WEEK1) $(PYTHON_BIN) -m flask run --port 3000

week2: 
	@eval "$$(pyenv init -)" && \
	FLASK_ENV=$(FLASK_ENV) FLASK_APP=$(WEEK2) $(PYTHON_BIN) -m flask run --port 3000

index: 
	./index-data.sh

delete:
	./delete-indexes.sh
	
download: 
	./download-data.sh