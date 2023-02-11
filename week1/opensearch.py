from flask import g, current_app
from opensearchpy import OpenSearch

host = 'localhost'
port = 9200
auth = ('admin', 'admin')

# Create an OpenSearch client instance and put it into Flask shared space for use by the application
def get_opensearch():
    if 'opensearch' not in g:
        #### Step 4.a:
        host = 'localhost'
        port = 9200
        auth = ('admin', 'admin')
        #### Step 2.a: Create a connection to OpenSearch
        g.opensearch = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_compress=True,
            http_auth=auth,
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )


    return g.opensearch
