import asyncio
import websockets
import http.cookies as cookies
from .events import *
from .objects import *
from .event_handler import event_handler
from .auth import validate_jwt, JWT_NAME
from .globals import *

# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50X2lkIjoiZWMzNWYyYTQtNTQ5OC00MWYwLTk4MTUtZWI3NjBiMjQzZDdjIiwiZXhwaXJlcyI6MTc4MDE1MTI4M30.WSq1rUB3fbnGfFAZhPiS2p8_q0ceuZTkq_9p4lkjfLA

async def connection_handler(ws: websockets.ServerConnection):
    player = None
    try:
        account_id = authenticate(ws)
        if account_id is None:
            await ws.send(ERROR_UNAUTHORIZED.json())
            print("CONNECTION: closed by server: Unauthorized")
            return
        player = await add_player(ws, account_id)
        if player is None:
            await ws.send(ERROR_LOBBY_FULL.json())
            print("CONNECTION: closed by server: Lobby full")
            return
        
        print("CONNECTION: opened")
        join_event = Event(eventType=EventType.PLAYER_JOIN, messageType=MsgType.REQUEST, details={"player": player})
        asyncio.create_task(event_handler(join_event, ws))
            
        async for payload in ws:
            try:
                request_event = Event.model_validate_json(payload)
                if request_event.eventType != EventType.PLAY_CARD:
                    continue
            except:
                await ws.send(ERROR_NOT_VALID_EVENT.json())
                continue
            asyncio.create_task(event_handler(request_event, ws))

    except websockets.ConnectionClosed:
        await remove_player(ws, player)
        print("CONNECTION: closed by client: Player left")
        leave_event = Event(eventType=EventType.PLAYER_LEAVE, messageType=MsgType.REQUEST, details={"player_id": player.player_id})
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
async def add_player(ws: websockets.ServerConnection, username: str):
    await state_lock.acquire()
    if len(game_state.players) < game_state.config.max_players:
        connections.add(ws)
        global next_player_id
        player = Player(next_player_id, username, 0)
        next_player_id += 1
        game_state.players.append(player)
        state_lock.release()
        return player
    else:
        state_lock.release()
        return None

# TODO : Remove player hand as well
async def remove_player(ws: websockets.ServerConnection, player: Player):
    await state_lock.acquire()
    game_state.players.remove(player)
    connections.remove(ws)
    state_lock.release()
        