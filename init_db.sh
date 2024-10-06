#!/bin/bash

PG_USER=$(jq -r '.pg_user' /app/config.json)
PG_PASSWORD=$(jq -r '.pg_password' /app/config.json)
PG_DB=$(jq -r '.pg_database' /app/config.json)

/usr/lib/postgresql/16/bin/postgres -D /var/lib/postgresql/data &

sleep 5

psql --command "CREATE USER $PG_USER WITH SUPERUSER PASSWORD '$PG_PASSWORD';"
createdb -O $PG_USER $PG_DB
pg_ctl -D /var/lib/postgresql/data -m fast -w stop