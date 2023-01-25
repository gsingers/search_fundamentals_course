# examples:
# To start flask server for week 1
# ./start-server.sh week1
# To start flask server for week 2
# ./start-server.sh week2

pyenv activate search_fundamentals
export FLASK_ENV=development
export FLASK_APP=$1
flask run --port 3000
