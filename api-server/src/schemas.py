from enum import Enum
from pydantic import BaseModel

class AccountStatus(str, Enum):
    offline = "offline"
    online = "online"


class Account(BaseModel):
    username : str
    password : str

class Statistic(BaseModel):
    account_username    : str
    status              : AccountStatus
    description         : str | None
    wins                : int
    losses              : int

class Friend(BaseModel):
    friend_status   : str