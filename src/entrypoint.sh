#!/usr/bin/env bash

echo "Hello"

if ! [[ -d "migrations" ]]
then
    flask db init
    echo "Init"

fi

echo "Migrate" 
flask db migrate

sleep 4

echo "Upgrade"
flask db upgrade

exec "$@"