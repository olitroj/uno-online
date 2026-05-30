import asyncio
from .objects import GameState, WsConnection

state_lock = asyncio.Lock()
game_state = GameState()
connections : list[WsConnection] = []