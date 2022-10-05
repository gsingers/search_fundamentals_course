# Welcome to Search Fundamentals

Search Fundamentals is a two week class taught by Grant Ingersoll and Daniel Tunkelang and is focused on helping students
quickly get up to speed on search by teaching the basics of search like indexing, querying, faceting/aggregations, spell checking, typeahead autocomplete and highlighting.

The class is a hands-on project-driven course where students will work with real data and the [Opensearch](https://opensearch.com)/Elasticsearch ecosystem.

# Class code layout (e.g. where the projects are)

For our class, we have two weekly projects.  Each project
is a standalone Python Flask application that interacts with an OpenSearch server (and perhaps other services).  

You will find these four projects in the directories below them organized in the following way:

- Week 1:
    - week1 -- The unfinished template for the week's project, annotated with instructions.
- Week 2:
    - week2 -- The unfinished template for the week's project, annotated with instructions.

Our instructor annotated results for each project will be provided during the class.  
Please note, these represent our way of doing the assignment and may differ from your results, 
as there is often more than one way of doing things in search.

You will also find several supporting directories and files for [Docker](https://docker.org) and [Gitpod](https://gitpod.io).

# Prerequisites

1. For this class, you will need a Kaggle account and a [Kaggle API token](https://www.kaggle.com/docs/api).
1. No prior search knowledge is required, but you should be able to code in Python or Java (all examples are in Python)
1. You will need a [Gitpod](https://gitpod.io) account.

# Working in Gitpod (Officially Supported)

1. Fork this repository.
1. Launch a new Gitpod workspace based on this repository.  This will automatically start OpenSearch and OpenSearch Dashboards.
    1. Note: it can take a few minutes for OpenSearch and the dashboards to launch.        
1. You should now have a running Opensearch instance (port 9200) and a running Opensearch Dashboards instance (port 5601)
1. Login to the dashboards at `https://5601-<$GITPOD_URL>/` with default username `admin` and password `admin`. This should popup automatically as a new tab, unless you have blocked popups.  Also note, that in the real world, you would change your password.  Since these ports are blocked if you aren't logged into Gitpod, it's OK.

        $GITPOD_URL is a placeholder for your ephemeral Gitpod host name, e.g. silver-grasshopper-8czadqyn.ws-us25.gitpod.io     

# Downloading the Best Buy Dataset

1. Run the install [Kaggle API token](https://www.kaggle.com/docs/api) script and follow the instructions:

        ./install-kaggle-token.sh
2. Accept all of the [kaggle competition rules](https://www.kaggle.com/c/acm-sf-chapter-hackathon-big/rules) then run the download data script:

        ./download-data.sh
3. Verify your data is in the right location: 
       
        ls /workspace/datasets
4. You should see:  `popular_skus.py  product_data  test.csv  train.csv`



# Exploring the OpenSearch Sample Dashboards and Data

1. Login to OpenSearch and point your browser at `https://5601-<$GITPOD_URL>/app/opensearch_dashboards_overview#/`
1. Click the "Add sample data" link
1. Click the "Add Data" link for any of the 3 projects listed. In the class, we chose the "Sample flight data", but any of the three are fine for exploration.

# Running the Weekly Project

At the command line, do the following steps to run the example.

1. Activate your Python Virtual Environment.  We use `pyenv` [Pyenv website](https://github.com/pyenv/pyenv) and `pyenv-virtualenv` [Pyenv Virtualenv](https://github.com/pyenv/pyenv-virtualenv), but you can use whatever you are most comfortable with.
    1. `pyenv activate search_fundamentals` -- Activate that Virtualenv. 
1. Run Flask: 
    1. `export FLASK_ENV=development`
    1.  *_IMPORTANT_* Set the Flask App Environment Variable for either `week1` or `week2`, depending on what you are working on, e.g.: `export FLASK_APP=week2`
    1. `flask run --port 3000` (or whatever port you choose) 
    1. Open the Flask APP at `https://3000-<$GITPOD_URL>/`  (or whatever port you choose)
1. Or run `ipython`
    
# Working locally (Not supported, but may work for you. YMMV)

To run locally, you will need a few things:

1. [Pyenv](https://github.com/pyenv/pyenv) and [Pyenv-Virtualenv](https://github.com/pyenv/pyenv-virtualenv) with Python 3.9.7 installed
1. [Docker](https://docker.com/)
1. A [Git](https://git-scm.com/) client

Note: these have only been tested on a Mac running OS 12.2.1.  YMMV.  Much of what you will need to do will be similar to what's in `.gitpod.Dockerfile`

1. `pyenv install 3.9.7`
1. `pip install` all of the libraries you see in `.gitpod.Dockerfile`
1. Setup your weekly python environments per the "Weekly Project" above.
1. Run OpenSearch: 
    1. `cd docker`
    1. `docker-compose up`
1. Note: most of the scripts and projects assume the data is in `/workspace/datasets`, but have overrides to specify your own directories. You will need to download and plan accordingly.  
1. Do your work per the Weekly Project     
    