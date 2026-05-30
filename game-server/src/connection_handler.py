import asyncio
import websockets
import http.cookies as cookies
from .objects import *
from .event_handler import event_handler
from .auth import validate_jwt, JWT_NAME
from .globals import *

async def connection_handler(conn: websockets.ServerConnection):
    ws = None
    try:
        account_id = authenticate(conn)
        if account_id is None:
            await conn.send(ERROR_UNAUTHORIZED.json())
            print("CONNECTION: closed by server: Unauthorized")
            return
        result = await add_player(conn, account_id)
        if not isinstance(result, WsConnection):
            await conn.send(result.json())
            print(f"CONNECTION: closed by server: {result.details.get("message")}")
            return
        ws = result
        
        print("CONNECTION: opened")
        join_event = Event(eventType=EventType.PLAYER_JOIN, messageType=MsgType.REQUEST, details={"player": ws.player})
        asyncio.create_task(event_handler(join_event, ws))
            
        async for payload in ws.conn:
            try:
                request_event = Event.model_validate_json(payload)
                if request_event.eventType != EventType.PLAY_CARD:
                    raise
            except:
                await ws.conn.send(ERROR_NOT_VALID_EVENT.json())
                continue
            asyncio.create_task(event_handler(request_event, ws))

    except websockets.ConnectionClosed:
        await remove_player(ws)
        print("CONNECTION: closed by client: Player left")
        leave_event = Event(eventType=EventType.PLAYER_LEAVE, messageType=MsgType.REQUEST, details={"player_id": ws.player.player_id})
        asyncio.create_task(event_handler(leave_event, ws))
 

def authenticate(ws: websockets.ServerConnection):
    try:
        cookie_header = ws.request.headers.get("cookie")
        cookie = cookies.SimpleCookie()
        cookie.load(cookie_header)
        token = cookie.get(JWT_NAME).value
        return validate_jwt(token)
    except:
        return None

# TODO : Check if the connection for that player already exists - Don't allow one player two connections
async def add_player(conn: websockets.ServerConnection, username: str):
    await state_lock.acquire()
    if len(game_state.players) >= game_state.config.max_players:
        state_lock.release()
        return ERROR_LOBBY_FULL
    elif game_state.stage != Stages.INTERMISSION:
        state_lock.release()
        return ERROR_GAME_STARTED
    
    player = Player(game_state.next_pid, username, 0)
    ws = WsConnection(player, conn)
    connections.append(ws)
    game_state.next_pid += 1
    game_state.players.append(player)
    state_lock.release()
    return ws

# TODO : Remove player hand as well
async def remove_player(ws: WsConnection):
    await state_lock.acquire()
    game_state.players.remove(ws.player)
    connections.remove(ws)
    state_lock.release()
        