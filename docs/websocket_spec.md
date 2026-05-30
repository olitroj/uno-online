# Websocket Specification

## Event Object

All communication between Clients and Server is done via Event Objects. Each event has an eventType, messageType and details related to the event. The eventType indicates the action performed, and the msgType refers to whether the message is a request (client -> server) or a response (server -> client).
```json
{
    "eventType": events,
    "messageType": types,
    "details": {...}
}
```

When a Client sends a request event, the Server determines it's validity based on the request details and the game's current state. If the request is valid, a response is echoed back to the client. The response may be broadcasted to other clients, or a different response may be broadcasted as well.

An example:
```json
Client -> Server
{
    "eventType": "PLAY_CARD",
    "messageType": "REQUEST",
    "details": {
        "card_id": 5
    }
}

Server -> Client
{
    "eventType": "PLAY_CARD",
    "messageType": "RESPONSE",
    "details": {
        "player_id": 1,
        "score": 15,
        "card": {
            "card_id": 10,
            "kind": "ONE",
            "color": "RED"
        },
        "turn": 2
    }
}
```

## Enums and Other Objects Reference
```json
stages: INTERMISSION, PLAY, END
types:  REQUEST, RESPONSE
kinds:  ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, ZERO, DRAW2, DRAW4, REVERSE, SKIP, WILD
colors: RED, GREEN, BLUE, YELLOW, NONE

Player {
    "player_id": int,
    "username:": str,
    "score": int
}
Config {
    "max_players": int,
    "timeout_sec": int,
    "start_cards": int
}
Card {
    "card_id": int,
    "kind": kinds,
    "color": colors
}
Hand {
    "player_id": int,
    "cards": [Card]
}
```

## Event Type Reference
```json
PLAYER_JOIN : {
    // Response
    "player": Player
}
PLAYER_LEAVE : {
    // Response
    "player_id": int
}
LOBBY_STATE : {
    // Response
    "players": [Player],
    "config": Config
}
GAME_START : {
    // Response
    "pile": Card,
    "turn": int,
    "hand": [Card]
}
PLAY_CARD : {
    // Request
    "card_id": int,
    "new_color": colors,
    // Response
    "player_id": int,
    "score": int,
    "card": Card,
    "turn": int,
}
DRAW_CARDS : {
    // Response
    "cards": [Card],
    "score": int
}
DREW_CARDS : {
    // Response
    "player_id": int,
    "score": int,
    "count": int
}
GAME_END : {
    // Response
    "leaderboard": [Player]
}
ERROR : {
    // Response
    "message": str
}
```