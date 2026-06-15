# UNO Multiplayer Online Card Game Project
## Oliver Trojanowski, Wint Kay Khine Myint, Chantelle Kwenda

## Architecture
![diagram](docs/uno_arch.drawio.svg)

API Server manages account creation, friending, and viewing player statistics and game history. Game server hosts game lobbies via websockets.

## Requirements
- Python 3.12 and pip
- Node 22 and npm
- Docker for running Postgres locally
- Docker compose for deployment
- CA certificate and private key pair for deployment

## Configuration
The project components require values from environment variables:
```sh
export JWT_NAME=""
export JWT_SECRET=""
export JWT_SESSION_LENGTH=

export POSTGRES_USER=""
export POSTGRES_PASSWORD=""
export POSTGRES_DB=""
```

When running locally `dev-env.sh` automatically exports these environment variables. \
When deploying, make sure to set these variables in `.env` in the project directory.

## Setting up local environment
This sets up the python and node environments by downloading all required dependencies
```sh
./dev-env.sh setup
```

## Running local environment
To start an individual component:
```sh
./dev-env.sh start [api|game|ui] [--db]
```
NOTE: Database container isn't automatically deleted when the script ends, remove it with `docker stop pg`.

The components are served on the following ports:
- REST API Server: http://localhost:8000
    - Swagger UI: http://localhost:8000/docs
- Gamer Server: ws://localhost:8080
    - Test Client: http://localhost:8888

- Frontend UI: http://localhost:5173

## Run Tests
```sh
./dev-env.sh test
```
The endpoint tests mock database calls, so they do not require a running database. The `--db` flag can be omitted.

## Deployment
First build the docker images:
```sh
docker compose build
```

Then, before starting the environment, create the previously mentioned environment variables and certificate/key files in the project directory:
- fullchain.pem
- privkey.pem
- .env

HINT: To generate a self-signed certificate use this command:
```sh
openssl req -x509 -newkey rsa:4096 -nodes -keyout privkey.pem -out fullchain.pem
```

Finally, start/stop the environment with:
```sh
docker compose up
docker compose down
```