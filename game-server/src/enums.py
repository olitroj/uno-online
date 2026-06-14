from enum import Enum

class Stages(Enum):
    INTERMISSION    = "INTERMISSION"
    PLAY            = "PLAY"
    END             = "END"

class Kind(Enum):
    ONE             = "ONE"
    TWO             = "TWO"
    THREE           = "THREE"
    FOUR            = "FOUR"
    FIVE            = "FIVE"
    SIX             = "SIX"
    SEVEN           = "SEVEN"
    EIGHT           = "EIGHT"
    NINE            = "NINE"
    ZERO            = "ZERO"
    DRAW2           = "DRAW2"
    DRAW4           = "DRAW4"
    REVERSE         = "REVERSE"
    SKIP            = "SKIP"
    WILD            = "WILD"

class Colors(Enum):
    RED             = "RED"
    GREEN           = "GREEN"
    BLUE            = "BLUE"
    YELLOW          = "YELLOW"
    NONE            = "NONE"

class EventType(Enum):
    PLAYER_JOIN     = "PLAYER_JOIN"
    PLAYER_LEAVE    = "PLAYER_LEAVE"
    LOBBY_STATE     = "LOBBY_STATE"
    GAME_START      = "GAME_START"
    PLAY_CARD       = "PLAY_CARD"
    DRAW_CARDS      = "DRAW_CARDS"
    DREW_CARDS      = "DREW_CARDS"
    TURN_TIMEOUT    = "TURN_TIMEOUT"
    GAME_END        = "GAME_END"
    GAME_RESTART    = "GAME_RESTART"
    ERROR           = "ERROR"

class MsgType(Enum):
    REQUEST         = "REQUEST"
    RESPONSE        = "RESPONSE"