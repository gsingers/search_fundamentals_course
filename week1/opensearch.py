from flask import g, current_app
from opensearchpy import OpenSearch
from index_products import get_opensearch

# Create an OpenSearch client instance and put it into Flask shared space for use by the application
def get_opensearch():
    if 'opensearch' not in g:
        #### Step 4.a:
        # Implement a client connection to OpenSearch so that the rest of the application can communicate with OpenSearch
        g.opensearch = get_opensearch()
        
    return g.opensearch
