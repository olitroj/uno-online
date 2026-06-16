// hooks/useGameSocket.ts — WebSocket connection and all game state.
//
// Manages the WebSocket to the game server and exposes gameState + action functions.
// The server never sends a full snapshot — we receive individual events and update
// state incrementally, which is why gameState has many separate fields.

import { useState, useEffect, useRef, useCallback } from 'react'
import type { GameState, Card, CardColor } from '@/types'

// The initial "blank" state — what the game looks like before we connect
const INITIAL_STATE: GameState = {
  stage: 'waiting',
  myPlayerId: null,
  myHand: [],
  pile: null,
  currentColor: 'NONE',
  turn: null,
  pendingDraw: 0,
  players: [],
  leaderboard: null,
  handSizes: {},
}

export function useGameSocket() {
  // gameState holds everything about the current game — updated as events arrive
  const [gameState, setGameState] = useState<GameState>(INITIAL_STATE)
  // error is shown as a banner at the top of the page
  const [error, setError] = useState<string | null>(null)
  // connected tracks whether the WebSocket is currently open
  const [connected, setConnected] = useState(false)

  const wsRef = useRef<WebSocket | null>(null)
  // Ref (not state) so onmessage handlers always read the latest player_id without stale closures.
  const myPlayerIdRef = useRef<number | null>(null)
  // Prevents React's dev-mode double-effect from opening two WebSocket connections.
  const didConnectRef = useRef(false)

  // Open the WebSocket once on mount.
  useEffect(() => {
    if (didConnectRef.current) return  // already ran — skip the second mount
    didConnectRef.current = true

    const ws = new WebSocket("/game")
    wsRef.current = ws

    ws.onopen  = () => setConnected(true)
    ws.onclose = () => { setConnected(false); didConnectRef.current = false }
    ws.onerror = () => setError('Connection to game server failed. Make sure the game server is running on port 8080.')

    // Every time the server sends us a message, parse the JSON and handle the event
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data as string)
        handleServerEvent(msg)
      } catch {
        console.error('Could not parse server message', event.data)
      }
    }

    // Cleanup: close the socket when the component unmounts (e.g. navigate away)
    return () => {
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close()
      }
    }
  }, [])

  // ── Event handler — called for every message from the server ──────────────

  function handleServerEvent(msg: { eventType: string; details: Record<string, unknown> }) {
    const { eventType, details } = msg

    // Server sent us an error — display it as a banner
    if (eventType === 'ERROR') {
      setError(details.message as string)
      return
    }

    // LOBBY_STATE — sent to us when we first join: the current player list
    if (eventType === 'LOBBY_STATE') {
      const players = details.players as Array<{ player_id: number; username: string; score: number }>
      setGameState(s => ({ ...s, players }))
      return
    }

    // PLAYER_JOIN — someone (possibly us) joined the lobby
    // We add them to the players list if they aren't already there
    if (eventType === 'PLAYER_JOIN') {
      const player = details.player as { player_id: number; username: string; score: number }
      setGameState(s => {
        const alreadyIn = s.players.find(p => p.player_id === player.player_id)
        if (alreadyIn) return s
        return { ...s, players: [...s.players, player] }
      })
      return
    }

    // PLAYER_LEAVE — someone disconnected; remove them from the list
    if (eventType === 'PLAYER_LEAVE') {
      const pid = details.player_id as number
      setGameState(s => ({ ...s, players: s.players.filter(p => p.player_id !== pid) }))
      return
    }

    // GAME_START — the game has begun.
    // The server sends us the starting pile card, who goes first, and OUR hand.
    // (Opponents' hands are never sent to us — only their card count.)
    if (eventType === 'GAME_START') {
      const pile = details.pile as Card
      const turn = details.turn as number
      const hand = details.hand as { player_id: number; cards: Card[] }

      myPlayerIdRef.current = hand.player_id

      setGameState(s => {
        // Initialise hand size tracking: everyone starts with 7 cards
        const initialSizes: Record<number, number> = {}
        s.players.forEach(p => { initialSizes[p.player_id] = 7 })
        initialSizes[hand.player_id] = hand.cards.length
        return {
          ...s,
          stage: 'playing',
          pile,
          currentColor: pile.color,
          turn,
          myPlayerId: hand.player_id,
          myHand: hand.cards,
          handSizes: initialSizes,
        }
      })
      return
    }

    // PLAY_CARD — any player (us or an opponent) just played a card.
    // We update: the pile, whose turn it is, active colour, pending draw,
    // the player's score, and (if it was an opponent) their hand size.
    if (eventType === 'PLAY_CARD') {
      const card        = details.card as Card
      const turn        = details.turn as number
      const currentColor = details.current_color as CardColor
      const pendingDraw = details.pending_draw as number
      const playerId    = details.player_id as number
      const score       = details.score as number

      setGameState(s => ({
        ...s,
        pile: card,
        currentColor,
        turn,
        pendingDraw,
        // If WE played the card, remove it from myHand; otherwise myHand is unchanged
        myHand: playerId === myPlayerIdRef.current
          ? s.myHand.filter(c => c.card_id !== card.card_id)
          : s.myHand,
        // Update that player's displayed score
        players: s.players.map(p => p.player_id === playerId ? { ...p, score } : p),
        // If an OPPONENT played, their hand shrank by 1
        handSizes: playerId !== myPlayerIdRef.current
          ? { ...s.handSizes, [playerId]: Math.max(0, (s.handSizes[playerId] ?? 7) - 1) }
          : s.handSizes,
      }))
      return
    }

    // DRAW_CARDS — sent ONLY to the player who drew (us).
    // Adds the drawn cards to our hand and advances the turn.
    if (eventType === 'DRAW_CARDS') {
      const drawnCards = details.cards as Card[]
      const score      = details.score as number
      const turn       = details.turn as number
      setGameState(s => ({
        ...s,
        myHand: [...s.myHand, ...drawnCards],
        pendingDraw: 0,
        turn,
        players: s.players.map(p =>
          p.player_id === myPlayerIdRef.current ? { ...p, score } : p
        ),
      }))
      return
    }

    // DREW_CARDS — broadcast to everyone EXCEPT the player who drew.
    // We don't see their cards — we only see how many they drew, so we can
    // update our local handSizes tracker.
    if (eventType === 'DREW_CARDS') {
      const pid       = details.player_id as number
      const score     = details.score as number
      const turn      = details.turn as number
      const drewCount = details.count as number
      setGameState(s => ({
        ...s,
        pendingDraw: 0,
        turn,
        players:   s.players.map(p => p.player_id === pid ? { ...p, score } : p),
        handSizes: { ...s.handSizes, [pid]: (s.handSizes[pid] ?? 7) + drewCount },
      }))
      return
    }

    // GAME_END — the game is over. The server sends the final leaderboard.
    if (eventType === 'GAME_END') {
      const leaderboard = details.leaderboard as Array<{ player_id: number; username: string; score: number }>
      setGameState(s => ({ ...s, stage: 'ended', leaderboard }))
      return
    }

    // GAME_RESTART — the lobby was reset; go back to the waiting state
    if (eventType === 'GAME_RESTART') {
      setGameState({ ...INITIAL_STATE })
      return
    }
  }

  // ── Actions — functions that send a message to the game server ────────────

  // Send: play one card from our hand (optionally with a chosen colour for Wild/Draw4)
  const playCard = useCallback((cardId: number, newColor: CardColor = 'NONE') => {
    wsRef.current?.send(JSON.stringify({
      eventType:   'PLAY_CARD',
      messageType: 'REQUEST',
      details: { card_id: cardId, new_color: newColor },
    }))
  }, [])

  // Send: draw card(s) from the deck (draws pendingDraw cards if +2/+4 is active, else 1)
  const drawCards = useCallback(() => {
    wsRef.current?.send(JSON.stringify({
      eventType:   'DRAW_CARDS',
      messageType: 'REQUEST',
      details: {},
    }))
  }, [])

  // Send: start the game (any player can trigger this when 2–4 players are in lobby)
  const startGame = useCallback(() => {
    wsRef.current?.send(JSON.stringify({
      eventType:   'GAME_START',
      messageType: 'REQUEST',
      details: {},
    }))
  }, [])

  return { gameState, playCard, drawCards, startGame, error, connected }
}
