import asyncio
import random
from datetime import datetime, timezone
from .objects import *
from .globals import *
from .db import db_query_one, db_execute


# ── Helpers ───────────────────────────────────────────────────────────────────

def card_to_dict(card: Card) -> dict:
    """Convert a Card dataclass to a plain dict (Enum values as strings)."""
    return {
        "card_id": card.card_id,
        "kind":    card.kind.value,
        "color":   card.color.value,
    }

def player_to_dict(player: Player) -> dict:
    return {"player_id": player.player_id, "username": player.username, "score": player.score}

def card_score(card: Card) -> int:
    """Point value of a card (used when calculating the winner's score)."""
    if card.kind in (Kind.WILD, Kind.DRAW4):
        return 50
    if card.kind in (Kind.SKIP, Kind.REVERSE, Kind.DRAW2):
        return 20
    number_map = {
        Kind.ZERO: 0, Kind.ONE: 1, Kind.TWO: 2, Kind.THREE: 3, Kind.FOUR: 4,
        Kind.FIVE: 5, Kind.SIX: 6, Kind.SEVEN: 7, Kind.EIGHT: 8, Kind.NINE: 9,
    }
    return number_map.get(card.kind, 0)

def is_playable(card: Card) -> bool:
    """Return True if the card can legally be played on the current pile."""
    if card.kind in (Kind.WILD, Kind.DRAW4):
        return True
    if card.color.value == game_state.current_color:
        return True
    if game_state.pile and card.kind == game_state.pile.kind:
        return True
    return False

def get_next_pid(skip: bool = False) -> int:
    """Return the player_id whose turn comes next. skip=True advances by 2."""
    players = game_state.players
    if not players:
        return -1
    current_idx = next((i for i, p in enumerate(players) if p.player_id == game_state.turn), 0)
    step = 2 if skip else 1
    next_idx = (current_idx + game_state.direction * step) % len(players)
    return players[next_idx].player_id

def score_for(player_id: int) -> int:
    """Sum of all cards in opponents' hands — the potential win score."""
    return sum(
        card_score(c)
        for h in game_state.hands
        for c in h.cards
        if h.player_id != player_id
    )

def ensure_deck() -> None:
    """If the draw deck is empty, reshuffle the played cards back into it."""
    if not game_state.deck and game_state.played_cards:
        game_state.deck = game_state.played_cards[:]
        game_state.played_cards.clear()
        random.shuffle(game_state.deck)

async def save_game_result(winner_id: int) -> None:
    """Insert one Games row and one Participants row per player."""
    end_time = datetime.now(timezone.utc)
    start_time = game_state.start_time or end_time

    # Create the game record and get the generated game_id back
    row = await db_query_one(
        "INSERT INTO Games (start_time, end_time) VALUES ($1, $2) RETURNING game_id",
        start_time, end_time
    )
    if row is None:
        return  # DB not available
    game_id = row["game_id"]

    # Insert a Participants record for every player
    for p in game_state.players:
        is_winner = (p.player_id == winner_id)
        final_score = p.score if is_winner else 0
        await db_execute(
            """INSERT INTO Participants (account_id, game_id, score, win)
               VALUES ($1::uuid, $2, $3, $4)""",
            p.account_id, game_id, final_score, is_winner
        )
        await db_execute(
            "UPDATE Accounts SET status='online' WHERE account_id = $1::uuid",
            p.account_id
        )


# ── Main event handler ────────────────────────────────────────────────────────

async def event_handler(event: Event, sender: WsConnection = None):
    print(f"EVENT: {event.eventType.value}")

    # ── PLAYER_JOIN ───────────────────────────────────────────────────────────
    if event.eventType == EventType.PLAYER_JOIN:
        await state_lock.acquire()
        event.messageType = MsgType.RESPONSE
        for ws in connections:
            if ws == sender:
                # Send the full lobby state only to the new player
                lobby_event = Event(
                    eventType=EventType.LOBBY_STATE,
                    messageType=MsgType.RESPONSE,
                    details={
                        "players": [player_to_dict(p) for p in game_state.players],
                        "config": {
                            "max_players": game_state.config.max_players,
                            "timeout_sec": game_state.config.timeout_sec,
                            "start_cards": game_state.config.start_cards,
                        },
                    },
                )
                await ws.conn.send(lobby_event.json())
            else:
                # Notify existing players that someone joined
                join_event = Event(
                    eventType=EventType.PLAYER_JOIN,
                    messageType=MsgType.RESPONSE,
                    details={"player": player_to_dict(sender.player)},
                )
                await ws.conn.send(join_event.json())

        state_lock.release()

    # ── PLAYER_LEAVE ──────────────────────────────────────────────────────────
    elif event.eventType == EventType.PLAYER_LEAVE:
        await state_lock.acquire()
        event.messageType = MsgType.RESPONSE
        for ws in connections:
            if ws != sender:
                await ws.conn.send(event.json())
        state_lock.release()

    # ── GAME_START ────────────────────────────────────────────────────────────
    elif event.eventType == EventType.GAME_START:
        await asyncio.sleep(3)   # small countdown before game begins
        await state_lock.acquire()
        enough_players = 2 <= len(game_state.players) <= game_state.config.max_players
        if enough_players and game_state.stage == Stages.INTERMISSION:
            game_state.stage = Stages.PLAY
            game_state.start_time = datetime.now(timezone.utc)

            create_handout_deck()

            # Keep drawing the first pile card until it's a number (avoid starting on an action)
            while True:
                game_state.pile = game_state.deck.pop()
                if game_state.pile.kind.value not in ("SKIP", "REVERSE", "DRAW2", "WILD", "DRAW4"):
                    break
                game_state.played_cards.append(game_state.pile)

            game_state.current_color = game_state.pile.color.value

            # Pick a random starting player
            starter = random.choice(game_state.players)
            game_state.turn = starter.player_id

            # Mark all players as in-game
            for p in game_state.players:
                await db_execute(
                    "UPDATE Accounts SET status='ingame' WHERE account_id = $1::uuid",
                    p.account_id
                )

            # Send GAME_START to each player with their own hand
            for ws in connections:
                hand = next(h for h in game_state.hands if h.player_id == ws.player.player_id)
                start_event = Event(
                    eventType=EventType.GAME_START,
                    messageType=MsgType.RESPONSE,
                    details={
                        "pile":  card_to_dict(game_state.pile),
                        "turn":  game_state.turn,
                        "hand":  {
                            "player_id": hand.player_id,
                            "cards": [card_to_dict(c) for c in hand.cards],
                        },
                    },
                )
                await ws.conn.send(start_event.json())

            print("GAME: started")
        state_lock.release()

    # ── PLAY_CARD ─────────────────────────────────────────────────────────────
    elif event.eventType == EventType.PLAY_CARD:
        await state_lock.acquire()

        # Guard: only valid during play phase and on the player's turn
        if game_state.stage != Stages.PLAY or game_state.turn != sender.player.player_id:
            await sender.conn.send(ERROR_FORBIDDEN.json())
            state_lock.release()
            return

        card_id   = event.details.get("card_id")
        new_color = event.details.get("new_color", "NONE")

        # Find the card in the sender's hand
        hand = next((h for h in game_state.hands if h.player_id == sender.player.player_id), None)
        card = next((c for c in hand.cards if c.card_id == card_id), None) if hand else None

        if card is None or not is_playable(card):
            await sender.conn.send(ERROR_FORBIDDEN.json())
            state_lock.release()
            return

        # Remove card from hand; move old pile card to played pile
        hand.cards.remove(card)
        if game_state.pile:
            game_state.played_cards.append(game_state.pile)
        game_state.pile = card

        # Update the active colour
        if card.kind in (Kind.WILD, Kind.DRAW4):
            game_state.current_color = new_color
        else:
            game_state.current_color = card.color.value

        # Apply card effects and decide whose turn is next
        skip = False
        if card.kind == Kind.SKIP:
            skip = True
        elif card.kind == Kind.REVERSE:
            game_state.direction *= -1
            # In a 2-player game, reverse acts like a skip
            if len(game_state.players) == 2:
                skip = True
        elif card.kind == Kind.DRAW2:
            # Turn goes TO the next player (skip=False).
            # They cannot play — pending_draw forces them to draw on their turn.
            game_state.pending_draw += 2
        elif card.kind == Kind.DRAW4:
            # Same as DRAW2: victim draws, then their turn ends automatically.
            game_state.pending_draw += 4

        game_state.turn = get_next_pid(skip=skip)

        # Calculate the sender's current potential score
        sender.player.score = score_for(sender.player.player_id)

        # Broadcast the played card to all players
        response = Event(
            eventType=EventType.PLAY_CARD,
            messageType=MsgType.RESPONSE,
            details={
                "player_id":    sender.player.player_id,
                "score":        sender.player.score,
                "card":         card_to_dict(card),
                "turn":         game_state.turn,
                "current_color": game_state.current_color,
                "pending_draw": game_state.pending_draw,
            },
        )
        for ws in connections:
            await ws.conn.send(response.json())

        # Check win condition
        if len(hand.cards) == 0:
            game_state.stage = Stages.END
            leaderboard = sorted(game_state.players, key=lambda p: p.score, reverse=True)
            end_event = Event(
                eventType=EventType.GAME_END,
                messageType=MsgType.RESPONSE,
                details={"leaderboard": [player_to_dict(p) for p in leaderboard]},
            )
            for ws in connections:
                await ws.conn.send(end_event.json())

            await save_game_result(winner_id=sender.player.player_id)
            print("GAME: ended")

        state_lock.release()

    # ── DRAW_CARDS ────────────────────────────────────────────────────────────
    elif event.eventType == EventType.DRAW_CARDS:
        await state_lock.acquire()

        if game_state.stage != Stages.PLAY or game_state.turn != sender.player.player_id:
            await sender.conn.send(ERROR_FORBIDDEN.json())
            state_lock.release()
            return

        # Draw pending_draw cards (from +2/+4) or just 1 if no penalty
        count = game_state.pending_draw if game_state.pending_draw > 0 else 1
        game_state.pending_draw = 0

        drawn = []
        for _ in range(count):
            ensure_deck()
            if game_state.deck:
                drawn.append(game_state.deck.pop())

        # Add drawn cards to the player's hand
        hand = next((h for h in game_state.hands if h.player_id == sender.player.player_id), None)
        if hand:
            hand.cards.extend(drawn)

        sender.player.score = score_for(sender.player.player_id)
        game_state.turn = get_next_pid()   # drawing ends the turn

        # Send the actual cards only to the player who drew
        draw_response = Event(
            eventType=EventType.DRAW_CARDS,
            messageType=MsgType.RESPONSE,
            details={
                "cards": [card_to_dict(c) for c in drawn],
                "score": sender.player.score,
                "turn":  game_state.turn,
            },
        )
        await sender.conn.send(draw_response.json())

        # Broadcast to others how many cards were drawn (not the actual cards)
        drew_event = Event(
            eventType=EventType.DREW_CARDS,
            messageType=MsgType.RESPONSE,
            details={
                "player_id": sender.player.player_id,
                "score":     sender.player.score,
                "count":     len(drawn),
                "turn":      game_state.turn,
            },
        )
        for ws in connections:
            if ws != sender:
                await ws.conn.send(drew_event.json())

        state_lock.release()

    # ── GAME_RESTART ──────────────────────────────────────────────────────────
    elif event.eventType == EventType.GAME_RESTART:
        await state_lock.acquire()
        # Reset game state but keep the player list
        old_players = game_state.players[:]
        game_state.__init__()
        game_state.players = old_players
        for p in game_state.players:
            p.score = 0

        restart_event = Event(
            eventType=EventType.GAME_RESTART,
            messageType=MsgType.RESPONSE,
            details={},
        )
        for ws in connections:
            await ws.conn.send(restart_event.json())
        state_lock.release()


# ── Deck creation ─────────────────────────────────────────────────────────────

def create_handout_deck():
    """Build a standard 108-card UNO deck, shuffle it, and deal starting hands."""
    card_id = 0
    deck: list[Card] = []

    for c in Colors:
        if c == Colors.NONE:
            continue
        # One zero per colour
        deck.append(Card(card_id, Kind.ZERO, c))
        card_id += 1

    for c in Colors:
        if c == Colors.NONE:
            continue
        # Two of each 1–9 and action card per colour
        for k in Kind:
            if k in (Kind.WILD, Kind.DRAW4, Kind.ZERO):
                continue
            deck.append(Card(card_id, k, c)); card_id += 1
            deck.append(Card(card_id, k, c)); card_id += 1

    # Four Wild and four Wild Draw 4 cards
    for _ in range(4):
        deck.append(Card(card_id, Kind.WILD,  Colors.NONE)); card_id += 1
        deck.append(Card(card_id, Kind.DRAW4, Colors.NONE)); card_id += 1

    random.shuffle(deck)

    # Deal starting hands
    for p in game_state.players:
        cards = [deck.pop() for _ in range(game_state.config.start_cards)]
        game_state.hands.append(Hand(p.player_id, cards))

    game_state.deck = deck
