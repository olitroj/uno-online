import websockets
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