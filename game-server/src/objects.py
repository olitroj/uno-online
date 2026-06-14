import websockets
from pydantic import BaseModel
from typing import Any
from dataclasses import dataclass
from datetime import datetime
from .enums import *

@dataclass
class Player():
    player_id   : int
    username    : str   # real display name fetched from the database
    account_id  : str   # UUID from Accounts table — used for DB writes
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
    max_players : int = 4
    timeout_sec : int = 60
    start_cards : int = 7

class GameState():
    def __init__(self):
        self.stage          : Stages        = Stages.INTERMISSION
        self.players        : list[Player]  = []
        self.next_pid       : int           = 0
        self.deck           : list[Card]    = []
        self.played_cards   : list[Card]    = []  # cards already played (for reshuffling)
        self.pile           : Card | None   = None
        self.current_color  : str           = "NONE"  # tracks active colour after wild
        self.turn           : int           = -1      # player_id whose turn it is
        self.direction      : int           = 1       # 1 = clockwise, -1 = counter-clockwise
        self.pending_draw   : int              = 0       # accumulated +2 / +4 cards
        self.hands          : list[Hand]       = []
        self.config         : Config           = Config()
        self.start_time     : datetime | None  = None   # set when PLAY stage begins
        self.turn_start_time: datetime | None  = None   # set when a turn begins (for timeout)

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
                                details={"message": "You have already joined"})
