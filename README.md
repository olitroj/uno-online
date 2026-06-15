# UNO Multiplayer Online Card Game Project
## Oliver Trojanowski, Wint Kay Khine Myint, Chantelle Kwenda

## Architecture
![diagram](docs/uno_arch.drawio.svg)

API Server manages account creation, friending, and viewing player statistics and game history. Game server hosts game lobbies via websockets.

## Requirements
- Python 3.13 or compatible Python 3 version
- Docker, for running PostgreSQL locally
- `pip`

## Configuration

The project components require values from environment variables:
```sh
export JWT_NAME="access_token"
export JWT_SECRET="9bxhAgLv4W5PhW4VNglCj4KQjEmLnLZy"
export JWT_SESSION_LENGTH=7200

export DB_USER="test_user"
export DB_PASS="test_password"
export DB_NAME="uno_db"
```

`dev-env.sh` exports the these environment variables automatically.

## Setting up local environment
This creates a python virtual environment and downloads all required dependencie
```sh
./dev-env.sh setup
```

## Running local environment
To start an individual component:\
NOTE: Database container isn't automatically deleted when the script ends, remove it with `docker stop pg`.
```sh
./dev-env.sh start [api|game] [--db]
```

The REST API is served at:
```text
API server
http://localhost:8000

Swagger UI
http://localhost:8000/docs
```

The Game is served at:
```text
Game server
ws://localhost:8080

Test client
http://localhost:8888
```

## Run Tests

```sh
./dev-env.sh test
```
The endpoint tests mock database calls, so they do not require --db flag.

## Deployment
Build the images with
```sh
docker compose build
```

Before starting the environment, create the following files under secrets/
- fullchain.pem
- privkey.pem
- .db.env
    - POSTGRES_USER
    - POSTGRES_PASSWORD
    - POSTGRES_DB
- .jwt.env
    - JWT_NAME
    - JWT_SECRET
    - JWT_SESSION_LENGTH

Start/Stop the environment with
```sh
docker compose up/down
```