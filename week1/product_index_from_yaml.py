import click
import yaml
import json


@click.command()
@click.option("--source_yaml", "-s", default="opensearch/bbuy_products_xml.yaml ")
@click.option("--out_json", "-o", default="opensearch/bbuy_products.json")
def main(source_yaml: str, out_json: str):
    """
    Creates an opensearch index definition file in json format from the yaml,
    The settings are added in front of the file and the "xml_field" properties are deletedgcv
    Args:
        source_yaml:
        out_json:
    """
    with open(source_yaml, "r") as f:
        source = yaml.safe_load(f)

    for mapping in source.values():
        del mapping["xml_field"]

    index_beginning = {
        "settings": {"index.refresh_interval": "5s"},
        "mappings": {"properties": source}}

    with open(out_json, "w") as f:
        json.dump(index_beginning, f, indent=2)


if __name__ == "__main__":
    main()
