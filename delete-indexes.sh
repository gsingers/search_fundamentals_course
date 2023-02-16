#!/bin/bash -e

if [ -f ".env" ]
then
  export $(grep -v '^#' .env | xargs)
  ES_CREDS=$ES_USER:$ES_PASS
else
  ES_CREDS=admin:admin
fi

BBUY_PRODUCTS_INDEX=https://localhost:9200/bbuy_products
BBUY_QUERIES_INDEX=https://localhost:9200/bbuy_queries

echo ""
echo "WARNING: Please note that this will delete the following OpenSearch indices."
echo "Will delete: $BBUY_PRODUCTS_INDEX"
echo "Will delete: $BBUY_QUERIES_INDEX"
echo ""
echo "Proceed? (y/N)"
read proceed

if [ "$proceed" != "y" ] && [ "$proceed" != "Y" ]
then
  echo "Aborted!"
  exit 1
fi

echo "Deleting products"
curl -k -X DELETE -u "$ES_CREDS" $BBUY_PRODUCTS_INDEX
echo ""
echo "Deleting queries"
curl -k -X DELETE -u "$ES_CREDS" $BBUY_QUERIES_INDEX

