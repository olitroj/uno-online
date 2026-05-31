import websockets
from pydantic import BaseModel
from typing import Any
from dataclasses import dataclass
from .enums import *

@dataclass
class Player():
    player_id   : int
    username    : str
    score       : int

@dataclass
class Card():
    card_id     : int
    kind        : Kind
    color       : Colors

@dataclass
class Hand():
    player_id   : int
    cards       : list[Card]

@dataclass
class Config():
    max_players : int = 2
    timeout_sec : int = 60
    start_cards : int = 7

class GameState():
    stage       : Stages        = Stages.INTERMISSION
    players     : list[Player]  = []
    next_pid    : int           = 0
    deck        : list[Card]    = []
    pile        : Card          = None
    turn        : int           = -1
    hands       : list[Hand]    = []
    config      : Config        = Config()

@dataclass
class WsConnection():
    player      : Player
    conn        : websockets.ServerConnection

class Event(BaseModel):
    eventType   : EventType
    messageType : MsgType
    details     : dict[str, Any]

    def json(self):
        return self.model_dump_json()

ERROR_NOT_VALID_EVENT   = Event(eventType=EventType.ERROR,
                                messageType=MsgType.RESPONSE,
                                details={"message": "Not a valid event"})
ERROR_UNAUTHORIZED      = Event(eventType=EventType.ERROR,
                                messageType=MsgType.RESPONSE,
                                details={"message": "Unauthorized"})
ERROR_LOBBY_FULL        = Event(eventType=EventType.ERROR,
                                messageType=MsgType.RESPONSE,
                                details={"message": "Lobby is full"})
ERROR_GAME_STARTED      = Event(eventType=EventType.ERROR,
                                messageType=MsgType.RESPONSE,
                                details={"message": "Game has already started"})
ERROR_ALREADY_CONNECTED = Event(eventType=EventType.ERROR,
                                messageType=MsgType.RESPONSE,
                                details={"message": "You are already connected"})
ERROR_FORBIDDEN         = Event(eventType=EventType.ERROR,
                                messageType=MsgType.RESPONSE,
                                details={"message": "This event is forbidden"})