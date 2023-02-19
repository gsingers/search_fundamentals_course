import math
# some helpful tools for dealing with queries
def create_stats_query(aggs, extended=True):
    print("Creating stats query from %s" % aggs)
    agg_map = {}
    agg_obj = {"aggs": agg_map, "size": 0}
    stats_type = "stats"
    if extended:
        stats_type = "extended_stats"
    for agg in aggs:
        agg_map[agg] = {stats_type: {"field": agg}}
    return agg_obj


# Hardcoded query here.  Better to use search templates or other query config.
def create_query(user_query, filters, sort="_score", sortDir="desc", size=10, include_aggs=True, highlight=True, source=None):
    query_obj = {
        'size': size,
        "sort":[
            {sort: {"order": sortDir}}
        ],
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": [

                        ],
                        "should":[ #
                            {
                                # Last gasp attempt at matching, based on the assumption the query is misspelled.
                              "match": {
                                    "name": {
                                        "query": user_query,
                                        "fuzziness": "1",
                                        "prefix_length": 2, # short words are often acronyms or usually not misspelled, so don't edit
                                        "boost": 0.01
                                    }
                               }
                            },
                            {
                              "match_phrase": { # near exact phrase match, so boost this higher
                                    "name.hyphens": {
                                        "query": user_query,
                                        "slop": 1,
                                        "boost": 50
                                    }
                               }
                            },
                            # General purpose query that searches across a number of fields
                            {
                              "multi_match": {
                                    "query": user_query,
                                    "type": "phrase",
                                    "slop": "6",
                                    "minimum_should_match": "2<75%",
                                    "fields": ["name^10", "name.hyphens^10", "shortDescription^5",
                                       "longDescription^5", "department^0.5", "sku", "manufacturer", "features", "categoryPath"]
                               }
                            },
                            {
                              "terms":{ # Lots of SKUs in the query logs, boost by it, split on whitespace so we get a list
                                "sku": user_query.split(),
                                "boost": 50.0
                              }
                            },
                            { # lots of products have hyphens in them or other weird casing things like iPad
                              "match": {
                                    "name.hyphens": {
                                        "query": user_query,
                                        "operator": "OR",
                                        "minimum_should_match": "2<75%"
                                    }
                               }
                            }
                        ],
                        "minimum_should_match": 1, # make sure at least one of the clauses above matches
                        "filter": filters  #
                    }
                },
                "boost_mode": "multiply", # how _score and functions are combined
                "score_mode": "sum", # how functions are combined
                # Use a scaled sales rank as factor in scoring.  This helps popular items rise to the top while still matching on keywords
                "functions": [
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankShortTerm"
                            }
                        },
                        "gauss": {
                            "salesRankShortTerm": {
                                "origin": "1.0",
                                "scale": "100"
                            }
                        }
                    },
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankMediumTerm"
                            }
                        },
                        "gauss": {
                            "salesRankMediumTerm": {
                                "origin": "1.0",
                                "scale": "1000"
                            }
                        }
                    },
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankLongTerm"
                            }
                        },
                        "gauss": {
                            "salesRankLongTerm": {
                                "origin": "1.0",
                                "scale": "1000"
                            }
                        }
                    },
                    {
                        "script_score": {
                            "script": "0.0001"
                        }
                    }
                ]

            }
        }
    }
    if user_query == "*" or user_query == "#":
        #replace the bool
        try:
            query_obj["query"] = {"match_all": {}}
        except:
            print("Couldn't replace query for *")
    if highlight:
        query_obj["highlight"] = {
            "fields": {
                "name": {},
                "shortDescription": {},
                "longDescription": {}
            }
        }
    if source is not None: # otherwise use the default and retrieve all source
        query_obj["_source"] = source

    if include_aggs:
        add_aggs(query_obj)
    return query_obj


##########
# Week 2, Level 2: 
##########
# Give a user query from the UI and the query object we've built so far, adding in spelling suggestions
def add_spelling_suggestions(query_obj, user_query):
    query_obj["suggest"] = {
       "text": user_query,
       "phrase_suggest": {
            "phrase": {
                "field": "suggest.trigrams",
                "direct_generator" : [
                    {
                        "field": "suggest.trigrams",
                        "suggest_mode": "popular",
                        "min_word_length": 2
                    }
                ],
                "highlight": {
                    "pre_tag": "<b>",
                    "post_tag": "</b>"
                }
            }
       },
       "term_suggest": {
            "term": {
                "field": "suggest.text",
                "suggest_mode": "popular",
                "min_word_length": 3
           }
       }
    }

    return query_obj


# Given the user query from the UI, the query object we've built so far and a Pandas data GroupBy data frame,
# construct and add a query that consists of the ids from the items that were clicked on by users for that query
# priors_gb (loaded in __init__.py) is grouped on query and has a Series of SKUs/doc ids for every document that was cliecked on for this query
def add_click_priors(query_obj, user_query, priors_gb):
    try:
        prior_clicks_for_query = priors_gb.get_group(user_query)
        if prior_clicks_for_query is not None and len(prior_clicks_for_query) > 0:
            click_prior = ""
            #### W2, L1, S1
            # Create a string object of SKUs and weights that will boost documents matching the SKU
            print("TODO: Implement me")
            if click_prior != "":
                click_prior_query_obj = None # Implement a query object that matches on the ID or SKU with weights of
                # This may feel like cheating, but it's really not, esp. in ecommerce where you have all this prior data,
                if click_prior_query_obj is not None:
                    query_obj["query"]["function_score"]["query"]["bool"]["should"].append(click_prior_query_obj)
    except KeyError as ke:
        print(ke)
        print(f"Can't process user_query: {user_query} for click priors")
        pass




def add_aggs(query_obj):
    query_obj["aggs"] = {
        "department": {
            "terms": {
                "field": "department.keyword",
                "min_doc_count": 1
            }
        },
        "missing_images": {
            "missing": {
                "field": "image"
            }
        },
        "regularPrice": {
            "range": {
                "field": "regularPrice",
                "ranges": [
                    {"key": "$", "to": 100},
                    {"key": "$$", "from": 100, "to": 200},
                    {"key": "$$$", "from": 200, "to": 300},
                    {"key": "$$$$", "from": 300, "to": 400},
                    {"key": "$$$$$", "from": 400, "to": 500},
                    {"key": "$$$$$$", "from": 500},
                ]
            },
            "aggs": {
                "price_stats": {
                    "stats": {"field": "regularPrice"}
                }
            }
        }

    }
