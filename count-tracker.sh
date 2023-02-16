#!/bin/bash -e

if [ -f ".env" ]
then
  export $(grep -v '^#' .env | xargs)
  ES_CREDS=$ES_USER:$ES_PASS
else
  ES_CREDS=admin:admin
fi

# A simple loop that can be run to check on counts for our two indices as you are indexing.  Ctrl-c to get out.
while [ true ];
do
  echo "Queries:"
  curl -k -XGET -u "$ES_CREDS"  "https://localhost:9200/_cat/count/bbuy_queries";
  echo "Products:"
  curl -k -XGET -u "$ES_CREDS"  "https://localhost:9200/_cat/count/bbuy_products";
  sleep 5;
done
