import asyncio
import random
from .objects import *
from .globals import *

async def event_handler(event: Event, sender: WsConnection = None):
    print(f"EVENT: registered event: {event.json()}")

    if event.eventType == EventType.PLAYER_JOIN:
        await state_lock.acquire()
        event.messageType = MsgType.RESPONSE
        for ws in connections:
            if ws == sender:
                lobby_state_event = Event(eventType=EventType.LOBBY_STATE, messageType=MsgType.RESPONSE,
                                          details={"players": game_state.players, "config": game_state.config})
                await ws.conn.send(lobby_state_event.json())
            else:
                await ws.conn.send(event.json())

        if len(game_state.players) == game_state.config.max_players:
            game_start_event = Event(eventType=EventType.GAME_START, messageType=MsgType.REQUEST, details={})
            asyncio.create_task(event_handler(game_start_event))
        state_lock.release()

    elif event.eventType == EventType.PLAYER_LEAVE:
        await state_lock.acquire()
        event.messageType = MsgType.RESPONSE
        for ws in connections:
            if ws != sender:
                await ws.conn.send(event.json())
        state_lock.release()
        
    elif event.eventType == EventType.GAME_START:
        await asyncio.sleep(5)
        await state_lock.acquire()
        if len(game_state.players) == game_state.config.max_players:
            game_state.stage = Stages.PLAY
            event.messageType = MsgType.RESPONSE
            
            create_handout_deck()
            game_state.pile = game_state.deck.pop()
            event.details["pile"] = game_state.pile
            event.details["turn"] = random.choice(game_state.players).player_id
            
            for ws in connections:
                for h in game_state.hands:
                    if h.player_id == ws.player.player_id:
                        event.details["hand"] = h
                        await ws.conn.send(event.json())
            print("GAME: game started")
        state_lock.release()


def create_handout_deck():
    card_id = 0
    for c in Colors:
        if c == Colors.NONE:
            continue
        game_state.deck.append(Card(card_id, Kind.ZERO, c))
        card_id += 1
    for c in Colors:
        if c == Colors.NONE:
            continue
        for k in Kind:
            if k == Kind.WILD or k == Kind.DRAW4 or k == Kind.ZERO:
                continue
            game_state.deck.append(Card(card_id, k, c))
            card_id += 1
            game_state.deck.append(Card(card_id, k, c))
            card_id += 1
    for _ in range(4):
        game_state.deck.append(Card(card_id, Kind.DRAW4, Colors.NONE))
        card_id += 1
        game_state.deck.append(Card(card_id, Kind.WILD, Colors.NONE))
        card_id += 1

    random.shuffle(game_state.deck)
    for p in game_state.players:
        cards = []
        for _ in range(game_state.config.start_cards):
            cards.append(game_state.deck.pop())
        game_state.hands.append(Hand(p.player_id, cards))