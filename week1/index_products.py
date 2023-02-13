# From https://github.com/dshvadskiy/search_with_machine_learning_course/blob/main/index_products.py
import opensearchpy
import requests
from lxml import etree

import click
import glob
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
import logging

from time import perf_counter
import concurrent.futures

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s')

# NOTE: this is not a complete list of fields.  If you wish to add more, put in the appropriate XPath expression.
#TODO: is there a way to do this using XPath/XSL Functions so that we don't have to maintain a big list?
mappings = {
    "productId": "productId/text()",
    "sku": "sku/text()",
    "name": "name/text()",
    "type": "type/text()",
    "startDate": "startDate/text()",
    "active": "active/text()",
    "regularPrice": "regularPrice/text()",
    "salePrice": "salePrice/text()",
    "artistName": "artistName/text()",
    "onSale": "onSale/text()",
    "digital": "digital/text()",
    "frequentlyPurchasedWith": "frequentlyPurchasedWith/*/text()",
    "accessories": "accessories/*/text()",
    "relatedProducts": "relatedProducts/*/text()",
    "crossSell": "crossSell/text()",
    "salesRankShortTerm": "salesRankShortTerm/text()",
    "salesRankMediumTerm": "salesRankMediumTerm/text()",
    "salesRankLongTerm": "salesRankLongTerm/text()",
    "bestSellingRank": "bestSellingRank/text()",
    "url": "url/text()",
    "categoryPath": "categoryPath/*/name/text()",
    "categoryPathIds": "categoryPath/*/id/text()",
    "categoryLeaf": "categoryPath/category[last()]/id/text()",
    "categoryPathCount": "count(categoryPath/*/name)",
    "customerReviewCount": "customerReviewCount/text()",
    "customerReviewAverage": "customerReviewAverage/text()",
    "inStoreAvailability": "inStoreAvailability/text()",
    "onlineAvailability": "onlineAvailability/text()",
    "releaseDate": "releaseDate/text()",
    "shippingCost": "shippingCost/text()",
    "shortDescription": "shortDescription/text()",
    "shortDescriptionHtml": "shortDescriptionHtml/text()",
    "class": "class/text()",
    "classId": "classId/text()",
    "subclass": "subclass/text()",
    "subclassId": "subclassId/text()",
    "department": "department/text()",
    "departmentId": "departmentId/text()",
    "bestBuyItemId": "bestBuyItemId/text()",
    "description": "description/text()",
    "manufacturer": "manufacturer/text()",
    "modelNumber": "modelNumber/text()",
    "image": "image/text()",
    "condition": "condition/text()",
    "inStorePickup": "inStorePickup/text()",
    "homeDelivery": "homeDelivery/text()",
    "quantityLimit": "quantityLimit/text()",
    "color": "color/text()",
    "depth": "depth/text()",
    "height": "height/text()",
    "weight": "weight/text()",
    "shippingWeight": "shippingWeight/text()",
    "width": "width/text()",
    "longDescription": "longDescription/text()",
    "longDescriptionHtml": "longDescriptionHtml/text()",
    "features": "features/*/text()",
}

def get_opensearch():
    host = 'localhost'
    port = 9200
    auth = ('admin', 'admin')
    #### Step 2.a: Create a connection to OpenSearch
    client = OpenSearch(
        hosts=[{"host": host, "port": port}],
        http_compress=True,
        http_auth=auth,
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        timeout=300,
    )
    return client


def index_file(file, index_name):
    docs_indexed = 0
    client = get_opensearch()
    logger.info(f'Processing file : {file}')
    tree = etree.parse(file)
    root = tree.getroot()
    children = root.findall("./product")
    docs = []
    for child in children:
        doc = {}
        for key, value in mappings.items():
            doc[key] = child.xpath(value)
        if 'productId' not in doc or len(doc['productId']) == 0:
            continue
        #### Step 2.b: Create a valid OpenSearch Doc and bulk index 2000 docs at a time
        doc["_index"] = index_name
        doc["_id"] = doc["sku"][0]
        docs_indexed += 1
        docs.append(doc)

        if docs_indexed % 2000 == 0:
            bulk(client, docs)
            logger.info(f"Indexed {docs_indexed} docs")
            docs = []
        
    if docs:
        bulk(client, docs)
        logger.info(f"Indexed {docs_indexed} docs")
        docs = []

    return docs_indexed

@click.command()
@click.option('--source_dir', '-s', help='XML files source directory')
@click.option('--index_name', '-i', default="bbuy_products", help="The name of the index to write to")
@click.option('--workers', '-w', default=8, help="The number of workers to use to process files")
def main(source_dir: str, index_name: str, workers: int):

    files = glob.glob(source_dir + "/*.xml")
    docs_indexed = 0
    start = perf_counter()
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(index_file, file, index_name) for file in files]
        for future in concurrent.futures.as_completed(futures):
            docs_indexed += future.result()

    finish = perf_counter()
    logger.info(f'Done. Total docs: {docs_indexed} in {(finish - start)/60} minutes')

if __name__ == "__main__":
    main()