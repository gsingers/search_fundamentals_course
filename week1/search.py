#
# The main search hooks for the Search Flask application.
#
import math
from flask import (
    Blueprint, redirect, render_template, request, url_for
)

from week1.opensearch import get_opensearch

bp = Blueprint('search', __name__, url_prefix='/search')


# Process the filters requested by the user and return a tuple that is appropriate for use in: the query, URLs displaying the filter and the display of the applied filters
# filters -- convert the URL GET structure into an OpenSearch filter query
# display_filters -- return an array of filters that are applied that is appropriate for display
# applied_filters -- return a String that is appropriate for inclusion in a URL as part of a query string.  This is basically the same as the input query string
def process_filters(filters_input):
    # Filters look like: &filter.name=regularPrice&regularPrice.key={{ agg.key }}&regularPrice.from={{ agg.from }}&regularPrice.to={{ agg.to }}
    filters = []
    display_filters = []  # Also create the text we will use to display the filters that are applied
    applied_filters = ""
    for filter in filters_input:
        type = request.args.get(filter + ".type")
        display_name = request.args.get(filter + ".displayName", filter)
        applied_filters += "&filter.name={}&{}.type={}&{}.displayName={}".format(filter, filter, type, filter,
                                                                                 display_name)
        if type == "range":
            from_val = request.args.get(filter + ".from", None)
            to_val = request.args.get(filter + ".to", None)
            print("from: {}, to: {}".format(from_val, to_val))
            # we need to turn the "to-from" syntax of aggregations to the "gte,lte" syntax of range filters.
            to_from = {}
            if from_val:
                to_from["gte"] = from_val
            else:
                from_val = "*"  # set it to * for display purposes, but don't use it in the query
            if to_val:
                to_from["lt"] = to_val
            else:
                to_val = "*"  # set it to * for display purposes, but don't use it in the query
            the_filter = {"range": {filter: to_from}}
            filters.append(the_filter)
            display_filters.append("{}: {} TO {}".format(display_name, from_val, to_val))
            applied_filters += "&{}.from={}&{}.to={}".format(filter, from_val, filter, to_val)
        elif type == "terms":
            field = request.args.get(filter + ".fieldName", filter)
            key = request.args.get(filter + ".key", None)
            the_filter = {"term": {field: key}}
            filters.append(the_filter)
            display_filters.append("{}: {}".format(display_name, key))
            applied_filters += "&{}.fieldName={}&{}.key={}".format(filter, field, filter, key)
    print("Filters: {}".format(filters))

    return filters, display_filters, applied_filters



# Our main query route.  Accepts POST (via the Search box) and GETs via the clicks on aggregations/facets
@bp.route('/query', methods=['GET', 'POST'])
def query():
    opensearch = get_opensearch() # Load up our OpenSearch client from the opensearch.py file.
    # Put in your code to query opensearch.  Set error as appropriate.
    error = None
    user_query = None
    query_obj = None
    display_filters = None
    applied_filters = ""
    filters = None
    sort = "_score"
    sortDir = "desc"
    unique_price_percentiles = [100, 200, 300, 400, 500]
    if request.method == 'POST':  # a query has been submitted
        user_query = request.form['query']
        if not user_query:
            user_query = "*"
        sort = request.form["sort"]
        if not sort:
            sort = "_score"
        sortDir = request.form["sortDir"]
        if not sortDir:
            sortDir = "desc"
    elif request.method == 'GET':  # Handle the case where there is no query or just loading the page
        user_query = request.args.get("query", "*")
        filters_input = request.args.getlist("filter.name")
        sort = request.args.get("sort", sort)
        sortDir = request.args.get("sortDir", sortDir)
        if filters_input:
            (filters, display_filters, applied_filters) = process_filters(filters_input)
    else:
        user_query = "*"

    #### Step 4.b.ii
    price_percentiles_query = create_price_percentiles_query(user_query, filters)
    price_percentiles_response = opensearch.search(body=price_percentiles_query, index="bbuy_products")
    unique_price_percentiles = sorted(list(set(dict(price_percentiles_response["aggregations"]["percentilesRegularPrice"]["values"]).values())))
    query_obj = create_query(user_query, filters, sort, sortDir, unique_price_percentiles)
    print("query obj: {}".format(query_obj))
    response = opensearch.search(body=query_obj, index="bbuy_products")
    # Postprocess results here if you so desire

    #print(response)
    if error is None:
        return render_template("search_results.jinja2", query=user_query, search_response=response,
                               display_filters=display_filters, applied_filters=applied_filters,
                               sort=sort, sortDir=sortDir)
    else:
        redirect(url_for("index"))


def create_search_query(user_query, filters):
    return {
        "size": 10,
        "query": {
            "bool": {
                "must": [
                    {
                        "query_string": { 
                            "query": user_query if user_query == '*' else f"\"{user_query}\"", 
                            "fields": ["name^100", "shortDescription^50", "longDescription^10", "department"],
                            "phrase_slop": 3
                        }
                    }
                ],
                "filter": filters if filters else [],
            }
        },
    }

def map_price_percentiles_to_ranges(unique_price_percentiles: list[int]):
    previous_value = 0
    ranges = []
    if len(unique_price_percentiles) == 1: 
        ranges.append({ "key": "$", "from": math.floor(unique_price_percentiles[0])})
    else:   
        for index, raw_value in enumerate(unique_price_percentiles):
            current_value = math.ceil(raw_value)
            if index == 0:
                ranges.append({'key':(index + 1) * '$', "to": current_value})
            else: 
                ranges.append({'key':(index + 1) * '$', 'from':previous_value, "to": current_value})

            previous_value = current_value
        ranges.append({'key':(len(unique_price_percentiles) + 1) * '$', 'from':previous_value})

    return ranges

def create_price_percentiles_query(user_query, filters):
    return {
        **create_search_query(user_query=user_query, filters=filters),
        "aggs": {
            "percentilesRegularPrice": {
                "percentiles": {
                    "field": "regularPrice", 
                    "percents": [25, 50, 75, 95, 99]         
                }
            }
        }
    }

def create_query(user_query, filters, sort, sortDir, unique_price_percentiles: list[int]):
    print("Query: {} Filters: {} Sort: {}".format(user_query, filters, sort))
    query_obj = {
        **create_search_query(user_query=user_query, filters=filters),
        "sort": [
            {
                f"{sort}": {
                    "order": sortDir
                }
            }
        ],

        "highlight" : {
            "pre_tags" : ["<mark>"],
            "post_tags" : ["</mark>"],
            "fields" : {
                "name" : {},
                "shortDescription":{},
                "longDescription": {},
                "department":{}
            }
        },
        ### Step 4.b.i: create the appropriate query and aggregations here
        "aggs": {
            "department": {
                "terms": {
                    "field": "department.keyword",
                    "min_doc_count": 1
                }
            },
            "missing_images": {
                "missing": {
                    "field": "image",
                }
            },
            "regularPrice": {
                "range": {
                    "field": "regularPrice",
                    "ranges": map_price_percentiles_to_ranges(unique_price_percentiles)
                },
            }
        }
    }
    return query_obj
