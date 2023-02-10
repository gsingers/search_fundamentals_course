# From https://github.com/dshvadskiy/search_with_machine_learning_course/blob/main/index_products.py
import opensearchpy
import requests
from lxml import etree

import click
import glob
import yaml
import json

from lxml.etree import Element
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
import logging

from time import perf_counter
import concurrent.futures

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
        ssl_show_warn=False)

    return client


def index_file(file, index_name, mappings):
    docs_indexed = 0
    client = get_opensearch()
    logger.info(f'Processing file : {file}')
    tree = etree.parse(file)
    root = tree.getroot()
    children = root.findall("./product")
    docs = []
    for child in children:
        doc = {}
        for key, val in mappings.items():
            doc[key] = child.xpath(val["xml_field"])
            if key == "crossSell" and len(doc[key]) > 0:
                print(doc[key])
        if 'productId' not in doc or len(doc['productId']) == 0:
            continue
        #### Step 2.b: Create a valid OpenSearch Doc and bulk index 2000 docs at a time
        the_doc = {#"_id": doc["productId"][0],
                   "_index": index_name
                   }

        for k, v in doc.items():
            the_doc[k] = v[0] if (isinstance(v, list) and len(v) == 1) else v
        docs.append(the_doc)

        if len(docs) == 2000:
            n_success, failures = bulk(client, docs)
            docs = []
            docs_indexed += n_success
            if failures:
                print(failures)
    # index the last elements which do not add up to 2000
    n_success, failures = bulk(client, docs)
    if failures:
        print(failures)
    docs_indexed += n_success

    return docs_indexed


def load_mappings():
    """
    The *.yaml file contains the mappings as opensearch expects it,
    plus a field "xml_field" which is used to extract the data from the xml docs
    """
    with open("opensearch/bbuy_products_xml.yaml", "r") as f:
        mappings = yaml.safe_load(f)
    return mappings


@click.command()
@click.option('--source_dir', '-s', help='XML files source directory')
@click.option('--index_name', '-i', default="bbuy_products", help="The name of the index to write to")
@click.option('--workers', '-w', default=8, help="The number of workers to use to process files")
@click.option("--number_of_files", "-n", type=int, help="Maximum number of files to process")
def main(source_dir: str, index_name: str, workers: int, number_of_files: int):
    files = glob.glob(source_dir + "/*.xml")

    if number_of_files:
        files = files[0:number_of_files]

    docs_indexed = 0
    start = perf_counter()

    mappings = load_mappings()

    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(index_file, file, index_name, mappings) for file in files]
        for future in concurrent.futures.as_completed(futures):
            docs_indexed += future.result()

    finish = perf_counter()
    logger.info(f'Done. Total docs: {docs_indexed} in {(finish - start) / 60} minutes')


if __name__ == "__main__":
    main()
