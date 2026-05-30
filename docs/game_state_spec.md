# Game State Specification

## Game State Object
The entire game state is represented by a single object stored on the **Server**. Class and Enum definitions can be found [here](websocket_spec.md#enums-and-other-objects-reference)
```json
{
    "stage": stages,
    "players": [Player],
    "pile": Card,
    "turn": int,
    "hands": [Hand],
    "config": Config
}
```

The game state is modified by Events occuring in the Game Loop. Some events are triggered by clients (namely PLAY_CARD and PLAYER_LEAVE).

## Game stages and General Loop
![Diagram](game_stages.drawio.svg)