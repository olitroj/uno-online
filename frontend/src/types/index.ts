// types/index.ts — ALL SHARED TYPESCRIPT TYPES used across the frontend.
//
// TypeScript "types" and "interfaces" are like contracts. They describe exactly
// what shape a piece of data must have. If you try to use a field that isn't in
// the type, TypeScript gives you an error before the code even runs.
//
// These types mirror the data returned by our API server and game server,
// so the names and values must match exactly (e.g. 'RED' not 'red').

// ── Card types (must match the game server's Python enums in enums.py) ─────────

// The four card colours plus NONE (used for Wild / Draw4 cards that have no colour)
export type CardColor = 'RED' | 'GREEN' | 'BLUE' | 'YELLOW' | 'NONE'

// Every possible card kind in a UNO deck
export type CardKind =
  | 'ZERO' | 'ONE' | 'TWO' | 'THREE' | 'FOUR'
  | 'FIVE' | 'SIX' | 'SEVEN' | 'EIGHT' | 'NINE'
  | 'SKIP' | 'REVERSE' | 'DRAW2' | 'WILD' | 'DRAW4'

// A single UNO card as sent by the game server
export interface Card {
  card_id: number    // unique ID so React can use it as a list key
  kind: CardKind
  color: CardColor
}

// ── Player / Account types (returned by the API server) ───────────────────────

// A player in a live game session (comes from the game server via WebSocket)
export interface Player {
  player_id: number   // temporary ID assigned by the game server for this session
  username: string
  score: number       // sum of card values remaining in opponents' hands
}

// The current user's full profile (returned by GET /me/info)
export interface AccountInfo {
  username: string
  status: 'online' | 'offline'
  description: string | null    // optional bio text
  wins: number
  losses: number
  total_score: number
}

// One row from the game history (returned by GET /me/games)
export interface GameRecord {
  start_time: string   // ISO date string, e.g. "2024-01-15T10:30:00Z"
  end_time: string
  score: number
  win: boolean
}

// One entry in the friends list (returned by GET /me/friends)
export interface Friend {
  username: string
  status: 'pending' | 'accepted' | 'rejected'
}

// ── Client-side game state (built up from WebSocket events) ───────────────────
//
// The game server never sends us the "full state" in one message.
// Instead it sends individual events (GAME_START, PLAY_CARD, etc.) and we
// build up this state object piece by piece inside useGameSocket.ts.

export interface GameState {
  // 'waiting'  = in the lobby, waiting for players
  // 'playing'  = game is active
  // 'ended'    = game finished, leaderboard is shown
  stage: 'waiting' | 'playing' | 'ended'

  myPlayerId: number | null         // our own player_id (set when GAME_START arrives)
  myHand: Card[]                    // our current hand of cards
  pile: Card | null                 // the top card on the discard pile
  currentColor: CardColor           // separate because playing a Wild changes the active color
                                    // without changing the card's own color (which stays NONE)
  turn: number | null               // player_id of whoever's turn it currently is
  pendingDraw: number               // how many cards the current player MUST draw (+2/+4 penalty)
  players: Player[]                 // all players in the game (including ourselves)
  leaderboard: Player[] | null      // sorted by score — only filled when game ends
  handSizes: Record<number, number> // maps player_id → number of cards in their hand
                                    // used to show face-down card stacks for opponents
}
