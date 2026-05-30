from pydantic import BaseModel
from typing import Any
from .enums import EventType, MsgType

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