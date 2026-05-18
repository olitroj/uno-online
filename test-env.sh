#!/bin/bash

# --- Config data --- #

export DB_USER="test_user"
export DB_PASS="test_password"
export DB_NAME="uno_db"
export HOST_NAME="localhost:8000"

rm -rf test.log &> /dev/null

# --- Start processes --- #

echo "Starting testing dependencies - PostgreSQL"

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

until docker exec pg pg_isready -U postgres &> /dev/null; do
  sleep 1
done


echo "Starting dev api-server"

cd api-server
uvicorn main:app &
API_SERVER_PID=$!

# --- Tests --- #

echo "Starting tests"
./test-endpoints.sh

# --- Cleanup --- #

kill $API_SERVER_PID
docker stop pg &> /dev/null