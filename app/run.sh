#!/bin/bash

if [ -z "${ES_HOST}" -o -z "${ES_PORT}" ]; then
    echo "[ERROR] envrinment var ES_HOST or ES_PORT not set."
    exit 1
fi

# wait for startup the elasticsearch
status='red'
while [ "$status" != "green" ]; do
    sleep 5
    res=$(curl -s ${ES_HOST}:${ES_PORT}/_cat/health?h=status)
    status=$(echo "$res" | sed -r 's/^[[:space:]]+|[[:space:]]+$//g') # trimmed status str is green or yellow or red.
    echo "elasticsearch status [$status]"
done

cd demo

## download data & ranklib
cp -rp ${APP_DIR_BASE}/app/demo/* .

## setup elasticsearch index
python index_tmdb.py --es-host "http://${ES_HOST}:${ES_PORT}"

sleep 5

## model train
python train.py --es-host "http://${ES_HOST}:${ES_PORT}"

echo "learning-to-rank setup is complemeted!!"
echo ""
echo "search..."

# search Rambo
keyword=Rambo
python check_search_results.py --keyword $keyword --es-host "http://${ES_HOST}:${ES_PORT}"

echo "DONE"
