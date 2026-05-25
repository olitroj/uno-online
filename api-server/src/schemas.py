from enum import Enum
from pydantic import BaseModel

class AccountStatus(str, Enum):
    offline     = "offline"
    online      = "online"
    ingame      = "ingame"

class FriendStatus(str, Enum):
    accepted    = "accepted"
    rejected    = "rejected"
    pending     = "pending"


class Account(BaseModel):
    username    : str
    password    : str
    status      : AccountStatus
    description : str | None

class AccountInfo(BaseModel):
    username    : str
    status      : AccountStatus
    description : str | None
    wins        : int
    losses      : int
    total_score : int

class Game(BaseModel):
    start_time  : int
    end_time    : int
    score       : int
    win         : bool

class Friend(BaseModel):
    username    : str
    status      : FriendStatus