#!/bin/bash

export JWT_NAME="access_token"
export JWT_SECRET="9bxhAgLv4W5PhW4VNglCj4KQjEmLnLZy" # Temporary for development, don't worry ;)
export JWT_SESSION_LENGTH=7200

start_db() {
    export DB_USER="test_user"
    export DB_PASS="test_password"
    export DB_NAME="uno_db"

    echo "Starting PostgreSQL..."

    docker run \
        --name pg \
        -e POSTGRES_USER=$DB_USER \
        -e POSTGRES_PASSWORD=$DB_PASS \
        -e POSTGRES_DB=$DB_NAME\
        -v ./db/init.sql:/docker-entrypoint-initdb.d/init.sql \
        -v ./db/seed.sql:/seed.sql \
        -p 5432:5432 \
        -d --rm \
        postgres

    db_exists=$?
    until docker exec pg pg_isready -U postgres 2>&1; do
        sleep 1
    done

    if [[ db_exists -eq 0 ]]; then
        docker exec pg psql "postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME" -f /seed.sql
    fi
}

start_api_server() {
    export SPEC_PATH="../docs/rest_specification.json"
    echo "Starting api-server..."
    cd ./api-server
    uvicorn main:app --reload
    cd ..
}

start_game_server() {
    export ENABLE_TEST_CLIENT="true"
    echo "Starting game-server"
    cd ./game-server
    python main.py
    cd ..
}

start_frontend() {
    echo "Starting frontend"
    cd ./frontend
    npm run dev
}

setup() {
    python -m venv .venv
    source .venv/Scripts/activate
    pip install -r ./api-server/requirements.txt -r ./game-server/requirements.txt
    cd ./frontend
    npm install
}

help() {
    echo "usage: ./dev-env.sh [setup|run|test] [api|game] [--db]"
    echo -e "\tsetup - Creates venv, download dependencies"
    echo -e "\trun - Run one of the following components"
    echo -e "\t\t- api - REST API server"
    echo -e "\t\t- game - Game server"
    echo -e "\ttest - Run unit tests"
    echo "Flags:"
    echo -e "\t--db - Run a PostgreSQL container alongside run command"
}

start() {
    if [[ "$2" == "--db" ]]; then
        start_db
    fi

    if [[ "$1" == "api" ]]; then
        start_api_server
    elif [[ "$1" == "game" ]]; then
        start_game_server
    else
        help
    fi
}

if [[ "$1" == "setup" ]]; then
    setup
elif [[ "$1" == "start" ]]; then
    start "$2" "$3"
elif [[ "$1" == "test" ]]; then
    pytest
else
    help
fi