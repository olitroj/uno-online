#!/bin/bash

start_db() {
    export DB_USER="test_user"
    export DB_PASS="test_password"
    export DB_NAME="uno_db"
    export HOST_NAME="localhost:8000"

    echo "Starting PostgreSQL..."

    docker run \
        --name pg \
        -e POSTGRES_USER=$DB_USER \
        -e POSTGRES_PASSWORD=$DB_PASS \
        -e POSTGRES_DB=$DB_NAME\
        -v ./conf/init.sql:/docker-entrypoint-initdb.d/init.sql \
        -p 5432:5432 \
        -d --rm \
        postgres

    if [[ $? -ne 0 ]]; then
        echo "ERROR: Failed to start PostgreSQL"
        exit 1
    fi

    until docker exec pg pg_isready -U postgres 2>&1; do
        sleep 1
    done
}

start_api_server() {
    cd ./api-server
    echo "Starting api-server..."
    uvicorn main:app --reload
}

start_api_server_tests() {
    cd ./api-server
    echo "Starting api-server tests..."
    pytest
}

action=0
for arg in "$@"; do
    if [[ "$arg" == "--db" ]]; then
        start_db
    elif [[ "$arg" == "--test" ]]; then
        action=1
    fi
done
if [[ $action -eq 0 ]]; then
    start_api_server
elif [[ $action -eq 1 ]]; then
    start_api_server_tests
fi