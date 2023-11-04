#!/bin/bash

PIDTEMP=$(ps ux | grep "python index_products.py" | grep -v "grep" | awk '{ print $2 }')
if [ "x$PIDTEMP" = "x" ]; then
  echo "Processes of index_products.py not found"
else
  echo "Killing index_products.py processes ..."
  kill -9 $PIDTEMP
fi

PIDTEMP=$(ps ux | grep "python index_queries.py" | grep -v "grep" | awk '{ print $2 }')
if [ "x$PIDTEMP" = "x" ]; then
  echo "Processes of index_queires.py not found"
else
  echo "Killing index_queires.py processes ..."
  kill -9 $PIDTEMP
fi

# Note:
# https://docs.python.org/3/library/concurrent.futures.html
# ProcessPoolExecutor does not support `thread_name_prefix` parameter.
# How can we reliably determine which processes are spawned by index-*.py scripts?
# For now, just kill everything that matches the generic string `multiprocessing-fork`
PIDTEMP=$(ps ux | grep "multiprocessing-fork" | grep -v "grep" | awk '{ print $2 }')
if [ "x$PIDTEMP" = "x" ]; then
  echo "No subprocesses are found"
else
  echo "Killing subprocessed ..."
  kill -9 $PIDTEMP
fi
