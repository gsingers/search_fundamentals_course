# WARNING: this will silently delete both of your indexes
echo "Deleting products"
curl -k -X DELETE "http://localhost:9200/bbuy_products"
echo ""
echo "Deleting queries"
curl -k -X DELETE "http://localhost:9200/bbuy_queries"

