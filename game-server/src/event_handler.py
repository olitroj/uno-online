import asyncio
import websockets
from .events import *
from .objects import *
from src.globals import game_state, connections, state_lock

async def event_handler(event: Event, sender: websockets.ServerConnection = None):
    print(f"EVENT: registered event: {event.json()}")

    if event.eventType == EventType.PLAYER_JOIN:
        event.messageType = MsgType.RESPONSE
        await state_lock.acquire()
        for ws in connections:
            if ws == sender:
                lobby_state_event = Event(eventType=EventType.LOBBY_STATE, messageType=MsgType.RESPONSE,
                                          details={"players": game_state.players, "config": game_state.config})
                await ws.send(lobby_state_event.json())
            else:
                await ws.send(event.json())

        if len(game_state.players) == game_state.config.max_players:
            game_start_event = Event(eventType=EventType.GAME_START, messageType=MsgType.REQUEST, details={})
            asyncio.create_task(event_handler(game_start_event))
        state_lock.release()

    elif event.eventType == EventType.PLAYER_LEAVE:
        event.messageType = MsgType.RESPONSE
        await state_lock.acquire()
        for ws in connections:
            if ws != sender:
                await ws.send(event.json())
        state_lock.release()
        
    elif event.eventType == EventType.GAME_START:
        await asyncio.sleep(5)
        await state_lock.acquire()
        if len(game_state.players) == game_state.config.max_players:
            game_state.stage = Stages.PLAY
            event.messageType = MsgType.RESPONSE
            for ws in connections:
                await ws.send(event.json())
        state_lock.release()
