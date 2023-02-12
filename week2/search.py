#
# The main search hooks for the Search Flask application.
#
from flask import (
    Blueprint, redirect, render_template, request, url_for, current_app
)

from week2.opensearch import get_opensearch

import week2.utilities.query_utils as qu

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
            if from_val and from_val != "*":
                to_from["gte"] = from_val
            else:
                from_val = "*"  # set it to * for display purposes, but don't use it in the query
            if to_val and to_val != "*":
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

@bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    results = {}
    if request.method == 'GET':  # a query has been submitted
        prefix = request.args.get("prefix")
        print(f"Prefix: {prefix}")
        if prefix is not None:
            type = request.args.get("type", "queries") # If type == queries, this is an autocomplete request, else if products, it's an instant search request.
            ##### W2, L3, S1
            search_response = None
            print("TODO: implement autocomplete AND instant search")
            if (search_response and search_response['suggest']['autocomplete'] and search_response['suggest']['autocomplete'][0]['length'] > 0): # just a query response
                results = search_response['suggest']['autocomplete'][0]['options']
    print(f"Results: {results}")
    return {"completions": results}

@bp.route('/query', methods=['GET', 'POST'])
def query():
    opensearch = get_opensearch()
    # Put in your code to query opensearch.  Set error as appropriate.
    error = None
    user_query = None
    query_obj = None
    display_filters = None
    applied_filters = ""
    filters = None
    sort = "_score"
    sortDir = "desc"

    autocompleteSelect = "queries"
    explain = False
    prior_clicks = current_app.config.get("priors_gb")
    if request.method == 'POST':  # a query has been submitted
        user_query = request.form['query']
        if not user_query:
            user_query = "*"
        autocompleteSelect = request.form["autocompleteSelect"]
        if not autocompleteSelect:
            autocompleteSelect = "queries"
        sort = request.form["sort"]
        if not sort:
            sort = "_score"
        sortDir = request.form["sortDir"]
        if not sortDir:
            sortDir = "desc"
        explain_val = request.form.get("explain", "false")
        if explain_val == "true":
            explain = True

        query_obj = qu.create_query(user_query,  [], sort, sortDir, size=20)  # We moved create_query to a utility class so we could use it elsewhere.
        ##### W2, L1, S2

        ##### W2, L2, S2
        print("Plain ol q: %s" % query_obj)
    elif request.method == 'GET':  # Handle the case where there is no query or just loading the page
        user_query = request.args.get("query", "*")
        filters_input = request.args.getlist("filter.name")
        sort = request.args.get("sort", sort)
        sortDir = request.args.get("sortDir", sortDir)
        explain_val = request.args.get("explain", "false")
        if explain_val == "true":
            explain = True
        if filters_input:
            (filters, display_filters, applied_filters) = process_filters(filters_input)
        query_obj = qu.create_query(user_query,  filters, sort, sortDir, size=20)
        #### W2, L1, S2

        ##### W2, L2, S2

    else:
        query_obj = qu.create_query("*", "", [], sort, sortDir, size=100)

    #print("query obj: {}".format(query_obj))
    response = opensearch.search(body=query_obj, index="bbuy_products", explain=explain)
    # Postprocess results here if you so desire

    #print(response)
    if error is None:
        return render_template("search_results.jinja2", query=user_query, search_response=response,
                               display_filters=display_filters, applied_filters=applied_filters,
                               sort=sort, sortDir=sortDir, explain=explain, autocompleteSelect=autocompleteSelect)
    else:
        redirect(url_for("index"))

