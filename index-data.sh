usage()
{
  echo "Usage: $0 [-d /path/to/kaggle/best/buy/datasets] [-p /path/to/bbuy/products/field/mappings] [ -q /path/to/bbuy/queries/field/mappings ] [ -g /path/to/write/logs/to ]"
  echo "Example: ./index-data "
  exit 2
}

PRODUCTS_JSON_FILE="/workspace/search_with_machine_learning_course/opensearch/bbuy_products.json"
QUERIES_JSON_FILE="/workspace/search_with_machine_learning_course/opensearch/bbuy_queries.json"
DATASETS_DIR="/workspace/datasets"


LOGS_DIR="/workspace/logs"

while getopts ':p:q:b:e:g:l:h' c
do
  case $c in
    p) PRODUCTS_JSON_FILE=$OPTARG ;;
    q) QUERIES_JSON_FILE=$OPTARG ;;
    d) DATASETS_DIR=$OPTARG ;;
    g) LOGS_DIR=$OPTARG ;;
    h) usage ;;
    [?]) usage ;;
  esac
done
shift $((OPTIND -1))


echo "Creating index settings and mappings"
echo " Product file: $PRODUCTS_JSON_FILE"
echo " Query file: $QUERIES_JSON_FILE"
curl -k -X PUT -u admin  "https://localhost:9200/bbuy_products" -H 'Content-Type: application/json' -d "@$PRODUCTS_JSON_FILE"
echo ""
curl -k -X PUT -u admin  "https://localhost:9200/bbuy_queries" -H 'Content-Type: application/json' -d "@$QUERIES_JSON_FILE"

cd utilities
echo "Indexing product data"
nohup python index_products.py -s "$DATASETS_DIR/product_data/products" > "$LOGS_DIR/index_products.log" &

echo "Indexing queries data"
nohup python index_queries.py -s "$DATASETS_DIR/train.csv" > "$LOGS_DIR/index_queries.log"" &