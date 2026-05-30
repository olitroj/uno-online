# Game Stages Specification
![Diagram](game_stages.drawio.svg)

### Intermission
When a client first attempts to join it will recieve a `LOBBY_STATE` event containing the current state of the lobby. The client will recieve an `ERROR` event, and the connection will be closed in the following circumstances:
- Client doesn't have a valid token (Unathorized)
- Lobby is full
- Game has already started (Not in Intermission stage)

When a client has joined, it will recieve `PLAYER_JOIN` and `PLAYER_LEFT` with information about the client who has joined/left. Once the lobby if full, a game will start after 5 seconds - signaled by the `GAME_START` event.

### Play
The `GAME_START` event contains details about the player's hand, the current pile card, and whose turn it is.

During this stage the server only listens for a `PLAY_CARD` event from the player whos turn it is. If a player sneds a `PLAY_CARD` when it is not their turn, they will recieve an `ERROR`. The player must play a card before the timeout (provided by `LOBBY_STATE` upon joining). If the player fails to play a card before the timeout, the server will play a random card from their hand for them. When a card has been played, the server broadcasts the `PLAY_CARD` event to all other clients. The server now listens to the next player, who is specified in the event details.

Players may recieve a `DRAW_CARDS` event before their turn starts if they cannot play any of their current cards, or it the previous player played either DRAW2 or DRAW4. When a player recieves `DRAW_CARDS`, all other players recieve a `DRAW_CARDS` event. The former specifies which cards the player recieves, while the latter states how many cards that player recieved.

When a client closes their connections:
- Their cards are removed from the game
- They are removed from the turn queue
- All other client recieve a `PLAYER_LEFT` event

Similarly, when a player plays all their cards, they are also removed from the turn queue. The turn queue keeps repeating until only one player remains in it. Then, the `GAME_END` event is served to all players.

### End
The `GAME_END` event contains details about each player, their score, and what place they one. The server waits 2 minutes for all clients to disconnect. If after 2 minutes some connections are still open, the server closes them. Then, the server clears the game state and goes back to the Intermission stage.