from opensearchpy import OpenSearch

def create_opensearch_client():
    host = 'localhost'
    port = 9200
    auth = ('admin', 'admin')
    #### Step 2.a: Create a connection to OpenSearch
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress = True,
        http_auth = auth,
        use_ssl=True,
        verify_certs = False,
        ssl_assert_hostname = False,
        ssl_show_warn = False
    )
    return client