# UNO Web App Project

REST API for account management, authentication, friend management, and game history.

## Requirements

- Python 3.13 or compatible Python 3 version
- Docker, for running PostgreSQL locally
- `pip`

## Configuration

The API reads configuration from environment variables:

```sh
export JWT_NAME="access_token"
export JWT_SECRET="9bxhAgLv4W5PhW4VNglCj4KQjEmLnLZy"
export JWT_SESSION_LENGTH=7200

export DB_USER="test_user"
export DB_PASS="test_password"
export DB_NAME="uno_db"
export HOST_NAME="localhost:8000"
```

`dev-env.sh` exports the JWT variables automatically. The database variables are exported when starting the database through that script.

## Install Dependencies

```sh
python3 -m pip install -r api-server/requirements.txt
```

## Run The API

Start PostgreSQL and initialize the schema:

```sh
./dev-env.sh start api --db
```

Or, if PostgreSQL is already running with the environment variables above:

```sh
cd api-server
uvicorn main:app --reload
```

The API is served at:

```text
http://localhost:8000
```

The OpenAPI specification is stored in:

```text
docs/rest_specification.json
```

## Run Tests

```sh
python3 -m pytest api-server/test/test_endpoints.py
```

The endpoint tests mock database calls, so they do not require PostgreSQL.
