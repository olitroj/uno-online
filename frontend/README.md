# Cat UNO — Multiplayer Card Game

A real-time multiplayer UNO card game with a cat theme, built with React + TypeScript + FastAPI + WebSockets.

---

## Prerequisites

- **Node.js** v20+
- **Python** 3.12+
- **PostgreSQL** 15+

---

## Environment Variables

Set these before starting the API server and game server (both must share the same JWT values):

```bash
export DB_USER=postgres
export DB_PASS=your_password
export DB_NAME=catunoapp
export JWT_NAME=auth_token
export JWT_SECRET=change_me_to_a_long_random_string
export JWT_SESSION_LENGTH=86400
```

---

## Database Setup (run once)

```bash
psql -U postgres -c "CREATE DATABASE catunoapp;"
psql -U postgres -d catunoapp -f db/init.sql
psql -U postgres -d catunoapp -f db/seed.sql   # optional test data
```

---

## Running the Application

Open **3 terminals** at the same time:

### Terminal 1 — API Server (port 8000)

```bash
cd api-server
source ../venv/bin/activate
pip install -r requirements.txt   # first time only
python3 main.py
```

### Terminal 2 — Game Server (port 8080)

```bash
cd game-server
source ../venv/bin/activate
pip install -r requirements.txt   # first time only
python3 main.py
```

### Terminal 3 — Frontend (port 5173)

```bash
cd frontend
npm install   # first time only
npm run dev
```

Open **http://localhost:5173** in your browser.  
Use two tabs or two different browsers to test multiplayer.

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
├── api-server/    REST API (FastAPI, Python)
├── game-server/   WebSocket game server (Python)
├── db/            SQL schema and seed data
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
