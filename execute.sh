#!/bin/bash

cd $(cd $(dirname $0) && pwd)

source .env

docker compose up -d aiac
docker compose exec aiac pip install -r /app/requirements.txt
docker compose exec aiac ./main.py
# docker compose exec aiac /bin/bash -l
