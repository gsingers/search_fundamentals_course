.PHONY: week1 week2 download delete index pyenv

export FLASK_ENV := development
export WEEK1 := week1
export WEEK2 := week2

pyenv:
	@eval "$$(pyenv init -)" && \
	pyenv activate search_fundamentals 

week1: 
	@eval "$$(pyenv init -)" && \
	pyenv activate search_fundamentals 
	FLASK_ENV=$(FLASK_ENV) FLASK_APP=$(WEEK1) flask run --port 3000 

week2: 
	@eval "$$(pyenv init -)" && \
	pyenv activate search_fundamentals 
	FLASK_ENV=$(FLASK_ENV) FLASK_APP=$(WEEK2) flask run --port 3000 
	

index: 
	./index-data.sh

delete:
	./delete-indexes.sh
	
download: 
	./download-data.sh