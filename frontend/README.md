# Cat UNO — Multiplayer Card Game

A real-time multiplayer UNO card game with a cat theme, built with React + TypeScript + FastAPI + WebSockets.

---

## Prerequisites

- **Node.js** v22+
- **Python** 3.12+
- **Docker** (for the PostgreSQL database)

---

## First-time Setup

Run this once from the project root to create the virtual environment and install all dependencies:

```bash
./dev-env.sh setup
```

This creates a `.venv/` folder and installs all Python and Node packages.

---

## Running the Application

Open **3 terminals** from the project root. Activate the Python virtual environment in each terminal that runs a Python server:

```bash
source .venv/bin/activate   # macOS / Linux
```

### Terminal 1 — Database + API Server

```bash
source .venv/bin/activate
./dev-env.sh start api --db
```

> The `--db` flag starts a PostgreSQL Docker container first, waits for it to be ready, then starts the API server.  
> Make sure Docker is running before this step.  
> To stop the database later: `docker stop pg`

- REST API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

### Terminal 2 — Game Server

```bash
source .venv/bin/activate
./dev-env.sh start game
```

- WebSocket: `ws://localhost:8080`
- Test client (browser UI for raw WebSocket testing): http://localhost:8888

### Terminal 3 — Frontend

```bash
./dev-env.sh start ui
```

- App: http://localhost:5173

The frontend proxies API and WebSocket requests automatically:
- `/me`, `/accounts` → API server at port 8000
- `/game` (WebSocket) → Game server at port 8080

Open **http://localhost:5173** in your browser.  
Use two tabs or two different browsers to test multiplayer.

---

## Run Tests

```bash
source .venv/bin/activate
./dev-env.sh test
```

Tests mock database calls, so no running database is needed.

---

## How to Play

1. Register an account in each browser tab
2. Click **Play Game** in both tabs
3. When 2–4 players are in the lobby, any player clicks **Start Game**
4. Click a glowing card to play it, or click the draw pile to draw
5. Wild / Draw4 cards open a colour picker
6. First player to empty their hand wins

---

## API Endpoints (12 total)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/me` | Register |
| `POST` | `/me/token` | Login |
| `DELETE` | `/me/token` | Logout |
| `GET` | `/me/info` | Get own profile |
| `PUT` | `/me` | Update profile |
| `DELETE` | `/me` | Delete account |
| `GET` | `/me/games` | Game history (paginated) |
| `GET` | `/me/friends` | Friends list (paginated + filtered) |
| `GET` | `/me/friends/count` | Total filtered friend count |
| `POST` | `/me/friends/{username}` | Send friend request |
| `PATCH` | `/me/friends/{username}` | Accept / reject request |
| `DELETE` | `/me/friends/{username}` | Remove friend |

---

## Project Structure

```
webapp-proj/
├── dev-env.sh     Helper script (setup / start / test)
├── .venv/         Shared Python virtual environment
├── api-server/    REST API (FastAPI, Python)
├── game-server/   WebSocket game server (Python)
├── db/            SQL schema and seed data
├── docs/          Architecture diagrams and API specs
└── frontend/      React + TypeScript app (this folder)
    └── src/
        ├── main.tsx                  Entry point
        ├── App.tsx                   Router
        ├── index.css                 Global styles
        ├── types/index.ts            TypeScript types
        ├── lib/api.ts                API call functions
        ├── lib/utils.ts              Tailwind class helper
        ├── hooks/useGameSocket.ts    WebSocket + game state
        ├── components/UnoCard.tsx    Card components
        ├── components/ui/            Button, Badge, Card, Input
        └── pages/                    AuthPage, HomePage, GamePage
```
