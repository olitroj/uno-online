import asyncio
import websockets
import http.cookies as cookies
from .objects import *
from .event_handler import event_handler
from .auth import validate_jwt, JWT_NAME
from .globals import *
from .db import db_query_one, db_execute

# Events that a client is allowed to send
ALLOWED_CLIENT_EVENTS = {EventType.PLAY_CARD, EventType.DRAW_CARDS, EventType.GAME_START}

async def connection_handler(conn: websockets.ServerConnection):
    ws = None
    try:
        account_id = authenticate(conn)
        if account_id is None:
            await conn.send(ERROR_UNAUTHORIZED.json())
            return

        result = await add_player(conn, account_id)
        if not isinstance(result, WsConnection):
            await conn.send(result.json())
            return

        ws = result
        await db_execute(
            "UPDATE Accounts SET status='online' WHERE account_id = $1::uuid",
            account_id
        )
        print(f"CONNECTION: opened for {ws.player.username}")

        # Announce the new player to the lobby
        join_event = Event(
            eventType=EventType.PLAYER_JOIN,
            messageType=MsgType.REQUEST,
            details={"player": {
                "player_id": ws.player.player_id,
                "username":  ws.player.username,
                "score":     ws.player.score,
            }},
        )
        asyncio.create_task(event_handler(join_event, ws))

        async for payload in ws.conn:
            try:
                request_event = Event.model_validate_json(payload)
            except Exception:
                await ws.conn.send(ERROR_NOT_VALID_EVENT.json())
                continue

            if request_event.eventType not in ALLOWED_CLIENT_EVENTS:
                await ws.conn.send(ERROR_FORBIDDEN.json())
                continue

            asyncio.create_task(event_handler(request_event, ws))

    finally:
        if ws is not None:
            await remove_player(ws)
            await db_execute(
                "UPDATE Accounts SET status='offline' WHERE account_id = $1::uuid",
                ws.player.account_id
            )
            print(f"CONNECTION: closed for {ws.player.username}")
            leave_event = Event(
                eventType=EventType.PLAYER_LEAVE,
                messageType=MsgType.REQUEST,
                details={"player_id": ws.player.player_id},
            )
            asyncio.create_task(event_handler(leave_event, ws))


def authenticate(conn: websockets.ServerConnection):
    """Extract and validate the JWT from the request cookie."""
    try:
        cookie_header = conn.request.headers.get("cookie", "")
        cookie = cookies.SimpleCookie()
        cookie.load(cookie_header)
        token = cookie[JWT_NAME].value
        return validate_jwt(token)
    except Exception:
        return None


async def add_player(conn: websockets.ServerConnection, account_id: str):
    # Fetch the real username from the database
    row = await db_query_one(
        "SELECT username FROM Accounts WHERE account_id = $1::uuid",
        account_id
    )
    if row is None:
        return ERROR_UNAUTHORIZED
    username = row["username"]

    await state_lock.acquire()

    # One account may only have one live websocket in the game. Removing the
    # old state here leaves the old websocket active and makes the lobby/game
    # inconsistent, so reject the second connection instead.
    existing_ws = next((w for w in connections if w.player.account_id == account_id), None)
    if existing_ws is not None:
        state_lock.release()
        return ERROR_ALREADY_CONNECTED

    if game_state.stage != Stages.INTERMISSION:
        state_lock.release()
        return ERROR_GAME_STARTED

    if len(game_state.players) >= game_state.config.max_players:
        state_lock.release()
        return ERROR_LOBBY_FULL

    player = Player(game_state.next_pid, username, account_id, 0)
    ws = WsConnection(player, conn)
    connections.append(ws)
    game_state.next_pid += 1
    game_state.players.append(player)
    state_lock.release()
    return ws


async def remove_player(ws: WsConnection):
    await state_lock.acquire()
    game_state.hands   = [h for h in game_state.hands   if h.player_id != ws.player.player_id]
    game_state.players = [p for p in game_state.players if p.player_id != ws.player.player_id]
    if ws in connections:
        connections.remove(ws)
    # When the last player leaves, reset everything so the next session can start fresh
    if len(connections) == 0:
        game_state.__init__()
    state_lock.release()
