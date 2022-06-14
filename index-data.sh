#!/usr/bin/env zsh

set -e
set -x

usage()
{
  echo "Usage: $0 [-y /path/to/python/indexing/code] [-d /path/to/kaggle/best/buy/datasets] [-p /path/to/bbuy/products/field/mappings] [ -q /path/to/bbuy/queries/field/mappings ] [ -g /path/to/write/logs/to ]"
  echo "Example: ./index-data.sh  -y /Users/grantingersoll/projects/corise/search_fundamentals_instructor/src/main/python/search_fundamentals/week1_finished   -d /Users/grantingersoll/projects/corise/datasets/bbuy -q /Users/grantingersoll/projects/corise/search_fundamentals_instructor/src/main/opensearch/bbuy_queries.json -p /Users/grantingersoll/projects/corise/search_fundamentals_instructor/src/main/opensearch/bbuy_products.json -g /tmp"
  exit 2
}

WORKDIR="/Users/tholland/search_fundamentals_course"
PRODUCTS_JSON_FILE="${WORKDIR}/opensearch/bbuy_products.json"
QUERIES_JSON_FILE="${WORKDIR}/opensearch/bbuy_queries.json"
CHECKPOINTS_DIR="${WORKDIR}/workspace/checkpoints"
DATASETS_DIR="${WORKDIR}/workspace/datasets"
PYTHON_LOC="${WORKDIR}/week1"

LOGS_DIR="${WORKDIR}/workspace/logs"

while getopts ':p:q:g:y:d:h' c
do
  case $c in
    p) PRODUCTS_JSON_FILE=$OPTARG ;;
    q) QUERIES_JSON_FILE=$OPTARG ;;
    d) DATASETS_DIR=$OPTARG ;;
    g) LOGS_DIR=$OPTARG ;;
    y) PYTHON_LOC=$OPTARG ;;
    h) usage ;;
    [?]) usage ;;
  esac
done
shift $((OPTIND -1))

mkdir -p $LOGS_DIR

echo "Creating index settings and mappings"
echo " Product file: $PRODUCTS_JSON_FILE"
curl -k -X PUT -u admin:admin  "https://localhost:9200/bbuy_products" -H 'Content-Type: application/json' -d "@$PRODUCTS_JSON_FILE"
if [ $? -ne 0 ] ; then
  echo "Failed to create index with settings of $PRODUCTS_JSON_FILE"
  exit 2
fi
echo ""
echo " Query file: $QUERIES_JSON_FILE"
curl -k -X PUT -u admin:admin  "https://localhost:9200/bbuy_queries" -H 'Content-Type: application/json' -d "@$QUERIES_JSON_FILE"
if [ $? -ne 0 ] ; then
  echo "Failed to create index with settings of $QUERIES_JSON_FILE"
  exit 2
fi

cd $PYTHON_LOC
python index_products.py -s "$DATASETS_DIR/product_data/products" --workers=6 -c "${CHECKPOINTS_DIR}"
echo ""
python index_queries.py -s "$DATASETS_DIR/train.csv"
