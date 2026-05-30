import asyncio
import websockets
from src.objects import GameState

state_lock = asyncio.Lock()
game_state = GameState()
connections : set[websockets.ServerConnection] = set()
next_player_id = 0