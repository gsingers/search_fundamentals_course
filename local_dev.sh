#!/bin/bash -e

if [ -f ".env" ]
then
  export $(grep -v '^#' .env | xargs)
fi

echo "Please review the settings below:"
echo "PRIOR_CLICKS_LOC=$PRIOR_CLICKS_LOC"
echo "PYTHON_BIN=$PYTHON_BIN"
echo "PRODUCTS_JSON_FILE=$PRODUCTS_JSON_FILE"
echo "QUERIES_JSON_FILE=$QUERIES_JSON_FILE"
echo "LOGS_DIR=$LOGS_DIR"

echo "Proceed? (y/N)"
read proceed

if [ "$proceed" != "y" ] && [ "$proceed" != "Y" ]; then
  echo "Aborted!"
  exit 1
fi

echo "Removing indices ..."
./stop-indexing.sh
./delete-indexes.sh

echo "Indexing data ..."
./index-data.sh \
  -p $PRODUCTS_JSON_FILE \
  -q $QUERIES_JSON_FILE \
  -d $DATASETS_DIR \
  -g $LOGS_DIR \
  -y $PYTHON_LOC

echo "To view logs, run the folllowing command:"
echo "tail -f $LOGS_DIR/*"
