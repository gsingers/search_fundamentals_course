# From Dmitiriy Shvadskiy https://github.com/dshvadskiy/search_with_machine_learning_course/blob/main/index_queries.py
# Modified for building suggesters
import click
import pandas as pd
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
import string

import logging
import time

# See https://pandas.pydata.org/docs/user_guide/index.html for Pandas help
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s')

def get_opensearch():

    host = 'localhost'
    port = 9200
    auth = ('admin', 'admin')
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=True,  # enables gzip compression for request bodies
        http_auth=auth,
        # client_cert = client_cert_path,
        # client_key = client_key_path,
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        #ca_certs=ca_certs_path
    )
    return client

@click.command()
@click.option('--source_file', '-s', help='source csv file', required=True)
@click.option('--index_name', '-i', default="bbuy_queries", help="The name of the index to write to")
def main(source_file: str, index_name: str):
    client = get_opensearch()
    # Load the data into a Pandas DataFrame
    df = pd.read_csv(source_file, keep_default_na=False, na_values={'category': {}})
    # Drop some columns we don't need.  We'll keep category for those who want to do more advanced suggesters that filter by category
    df.drop("click_time", axis=1, inplace=True)
    df.drop("query_time", axis=1, inplace=True)
    df.drop("user", axis=1, inplace=True)

    # Do some clean up work on our data for indexing.
    # Keep in mind, the main thing we are trying to build here is a good suggester, as we are not using these queries
    # for anything else in this class.  If you want to see how to use queries to make your ranking better,
    # check out our Search with Machine Learning class: https://corise.com/course/search-with-machine-learning?utm_source=daniel.
    # Let's create a field just for suggestions.
    # As there are a lot of near duplicate queries in these logs that only differ by case, let's lowercase them
    df["suggest"] = df["query"].str.lower()
    suggest_gb = df.groupby("suggest")
    # Advanced level: figure out associated words and put them in the same input per https://www.elastic.co/blog/you-complete-me
    # for instance, office and "microsoft office" might go together

    # Let's add the number of times we've seen this query in our click logs as an approximation of how popular that query is


    #print(ds.dtypes)
    docs = []
    tic = time.perf_counter()
    for suggest, group in suggest_gb:
        unique = group["query"].unique().tolist()
        canonical = unique[0].strip().title().encode("ascii", "ignore").decode()
        doc = {
            "query": unique,
            "suggest": {
                "weight": group["query"].count(), # get the number of times a query has a click and use that as a weight.
                "input": unique
            },
            "sku": group["sku"].unique().tolist(),
            "canonical": canonical,
            "category": group["category"].unique().tolist()
        }
        docs.append({'_index': index_name , '_source': doc})
        if len(docs) % 10 == 0:
            bulk(client, docs, request_timeout=60)
            docs = []
    if len(docs) > 0:
        bulk(client, docs, request_timeout=60)
    toc = time.perf_counter()
    logger.info(f'Done indexing {df.shape[0]} records. Total time: {((toc-tic)/60):0.3f} mins.')

if __name__ == "__main__":
    main()