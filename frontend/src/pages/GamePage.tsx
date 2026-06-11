// pages/GamePage.tsx — THE GAME BOARD (route: "/game")
//
// This page has three visual "stages" controlled by gameState.stage:
//
//   'waiting' — lobby screen: shows players in the lobby and a "Start Game" button
//   'playing' — active game board: opponents' cards, draw pile, discard pile, your hand
//   'ended'   — results overlay: leaderboard with medals and score
//
// All game logic and WebSocket communication is in useGameSocket.ts.
// This file only handles what to SHOW and what to DO when the user clicks something.
//
// CLIENT-SIDE PLAYABILITY CHECK (isPlayable):
//   The server enforces the real rules, but we also check on the client so we can
//   highlight playable cards (green glow) and block clicks on unplayable ones.
//   This makes the UI feel responsive — no network round-trip needed to grey out cards.
//
// WILD CARD FLOW:
//   1. Player clicks a Wild or Draw4 card
//   2. We store it in pendingWild state and show the colour picker dialog
//   3. Player picks a colour → handleColorPick() → playCard(cardId, chosenColor)
//   4. The colour picker closes (pendingWild = null)

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useGameSocket } from '@/hooks/useGameSocket'
import { UnoCard, CardBack, CardSlot } from '@/components/UnoCard'
import { Button } from '@/components/ui/Button'
import type { Card, CardColor } from '@/types'
import { ArrowLeft } from 'lucide-react'

// The four colours a player can pick after playing a Wild or Draw4
const WILD_COLORS: { color: CardColor; bg: string; label: string }[] = [
  { color: 'RED',    bg: 'bg-red-500',    label: '🔴 Red'    },
  { color: 'GREEN',  bg: 'bg-green-600',  label: '🟢 Green'  },
  { color: 'BLUE',   bg: 'bg-blue-600',   label: '🔵 Blue'   },
  { color: 'YELLOW', bg: 'bg-yellow-400', label: '🟡 Yellow' },
]

// Returns true if the given card can legally be played right now.
// This mirrors the server-side is_playable() in event_handler.py so the UI
// stays in sync with the server rules without an extra network call.
function isPlayable(card: Card, pileColor: CardColor, pileKind: string, pendingDraw: number): boolean {
  // If there is a pending +2/+4 penalty, the player MUST draw — no playing allowed
  if (pendingDraw > 0) return false
  // Wild and Draw4 can always be played (on any colour)
  if (card.kind === 'WILD' || card.kind === 'DRAW4') return true
  // Same colour as the current active colour
  if (card.color === pileColor) return true
  // Same kind/number as the top pile card (e.g. any RED 7 on a BLUE 7)
  if (card.kind === pileKind) return true
  return false
}

export default function GamePage() {
  const navigate = useNavigate()

  // Get game state and action functions from the WebSocket hook
  const { gameState, playCard, drawCards, startGame, error, connected } = useGameSocket()

  // If the player clicks a Wild/Draw4, store it here while showing the colour picker.
  // null = colour picker is closed.
  const [pendingWild, setPendingWild] = useState<Card | null>(null)

  // Destructure the game state into individual variables for easier use below
  const { stage, myPlayerId, myHand, pile, currentColor, turn, pendingDraw, players, leaderboard, handSizes } = gameState
  const isMyTurn  = turn === myPlayerId
  const opponents = players.filter(p => p.player_id !== myPlayerId)  // everyone except me
  const me        = players.find(p => p.player_id === myPlayerId)

  // Called when the player clicks a card in their hand
  function handleCardClick(card: Card) {
    if (!isMyTurn) return      // not your turn — do nothing
    if (!pile) return           // no pile card yet — shouldn't happen

    const canPlay = isPlayable(card, currentColor, pile.kind, pendingDraw)
    if (!canPlay) return        // card is not legal to play right now

    if (card.kind === 'WILD' || card.kind === 'DRAW4') {
      // Wild cards need a colour choice before we can send the play to the server
      setPendingWild(card)      // open the colour picker dialog
    } else {
      playCard(card.card_id)    // send PLAY_CARD event to game server
    }
  }

  // Called when the player picks a colour in the Wild colour picker dialog
  function handleColorPick(color: CardColor) {
    if (!pendingWild) return
    playCard(pendingWild.card_id, color)   // send PLAY_CARD with the chosen colour
    setPendingWild(null)                   // close the dialog
  }

  // CSS class for the coloured dot showing the current active colour
  const colorDotClass: Record<CardColor, string> = {
    RED:    'bg-red-500',
    GREEN:  'bg-green-600',
    BLUE:   'bg-blue-600',
    YELLOW: 'bg-yellow-400',
    NONE:   'bg-gray-600',
  }

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-[#0a0a0f] flex flex-col">

      {/* Top bar — always visible */}
      <header className="border-b border-[#2a2a4a] bg-[#12121f] px-4 py-2 flex items-center gap-3">
        <button onClick={() => navigate('/home')} className="text-[#888899] hover:text-white transition-colors">
          <ArrowLeft size={18} />
        </button>
        <span className="font-bold text-white text-sm">Cat UNO</span>
        {/* Green dot = connected to game server, red dot = disconnected */}
        <div
          className={`ml-auto w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}
          title={connected ? 'Connected' : 'Disconnected'}
        />
      </header>

      {/* Error banner — shown when the game server sends an ERROR event */}
      {error && (
        <div className="bg-[#3a1a1a] border-b border-[#e05555]/40 px-4 py-2 text-sm text-[#e05555] text-center">
          {error}
        </div>
      )}

      {/* ── WAITING STAGE — lobby ───────────────────────────────────────── */}
      {stage === 'waiting' && (
        <div className="flex-1 flex flex-col items-center justify-center gap-6 p-8">
          <div className="text-6xl animate-bounce">🐱</div>
          <div className="text-center">
            <h2 className="text-xl font-bold text-white mb-1">Lobby</h2>
            <p className="text-[#888899] text-sm">
              {players.length < 2
                ? 'Waiting for more players… (need at least 2)'
                : `${players.length} player${players.length > 1 ? 's' : ''} ready — you can start!`}
            </p>
          </div>

          {/* List of players currently in the lobby */}
          {players.length > 0 && (
            <div className="flex flex-col gap-2 text-sm w-full max-w-xs">
              {players.map(p => (
                <div key={p.player_id} className="flex items-center gap-2 bg-[#1a1a2e] px-4 py-2 rounded-lg">
                  <span className="text-lg">🐱</span>
                  <span className="text-white">{p.username}</span>
                  {p.player_id === myPlayerId && <span className="text-xs text-[#6c63ff]">(you)</span>}
                </div>
              ))}
            </div>
          )}

          {/* Start Game button — only visible once 2+ players are in the lobby.
              Any player can press it; the game server verifies the player count. */}
          {players.length >= 2 && (
            <Button size="lg" onClick={startGame} className="w-full max-w-xs">
              Start Game ({players.length}/4)
            </Button>
          )}

          <Button variant="ghost" onClick={() => navigate('/home')}>← Back to home</Button>
        </div>
      )}

      {/* ── PLAYING STAGE — the game board ─────────────────────────────── */}
      {stage === 'playing' && (
        <div className="flex-1 flex flex-col p-3 gap-3 overflow-hidden">

          {/* Opponents area — one panel per opponent (works for 2, 3, or 4 players) */}
          <div className="flex flex-col gap-2">
            {opponents.map(opp => {
              const cardCount   = handSizes[opp.player_id] ?? 7  // how many cards they have
              const isTheirTurn = turn === opp.player_id
              return (
                <div key={opp.player_id} className="flex items-center justify-between bg-[#1a1a2e] rounded-xl px-4 py-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">🐱</span>
                    <div>
                      <div className="text-sm font-bold text-white">{opp.username}</div>
                      <div className="text-xs text-[#888899]">{cardCount} card{cardCount !== 1 ? 's' : ''}</div>
                    </div>
                  </div>
                  {/* Show up to 5 face-down cards; if more, show a "+N" count */}
                  <div className="flex items-center gap-2">
                    {Array.from({ length: Math.min(5, cardCount) }).map((_, i) => (
                      <CardBack key={i} size="sm" />
                    ))}
                    {cardCount > 5 && (
                      <span className="text-sm font-bold text-[#888899]">+{cardCount - 5}</span>
                    )}
                  </div>
                  {/* "Thinking…" shown only when it's this opponent's turn */}
                  {isTheirTurn && (
                    <div className="text-xs text-[#f0a030] font-semibold pulse-ring px-2 py-1 rounded">
                      Thinking…
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {/* Centre: draw pile + discard pile + turn info */}
          <div className="flex-1 flex items-center justify-center">
            <div className="flex items-center gap-6 md:gap-10">

              {/* Draw pile — clicking it sends a DRAW_CARDS event to the server */}
              <div className="flex flex-col items-center gap-2">
                <CardBack
                  size="lg"
                  onClick={isMyTurn ? drawCards : undefined}   // only clickable on my turn
                  className={isMyTurn ? 'card-playable' : 'opacity-50'}
                />
                <span className="text-xs text-[#888899]">Draw pile</span>
                {/* Warn the player when they MUST draw (pending +2 or +4 penalty) */}
                {pendingDraw > 0 && (
                  <span className="text-xs font-bold text-[#e05555]">Draw +{pendingDraw}!</span>
                )}
              </div>

              {/* Discard pile — shows the current top card */}
              <div className="flex flex-col items-center gap-2">
                {pile
                  ? <UnoCard card={pile} displayColor={currentColor} size="lg" />
                  : <CardSlot size="lg" label="Pile" />
                }
                {/* Coloured dot shows the active colour (important after a Wild is played) */}
                <div className="flex items-center gap-1.5">
                  <div className={`w-3 h-3 rounded-full ${colorDotClass[currentColor]}`} />
                  <span className="text-xs text-[#888899] capitalize">{currentColor.toLowerCase()}</span>
                </div>
              </div>

              {/* Turn / status panel */}
              <div className="flex flex-col items-center gap-2 text-center">
                <div className={`px-3 py-2 rounded-xl text-sm font-bold ${
                  isMyTurn
                    ? 'bg-[#1e2e1e] text-[#55c48a] pulse-ring'
                    : 'bg-[#1a1a2e] text-[#888899]'
                }`}>
                  {isMyTurn ? '✨ Your turn!' : "Opponent's turn"}
                </div>
                {/* UNO badge — shown when the player has exactly 1 card left */}
                {myHand.length === 1 && isMyTurn && (
                  <div className="mt-1 px-4 py-2 bg-[#e05555] rounded-full text-white font-black text-sm animate-pulse">
                    UNO! 🃏
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Player's hand — horizontally scrollable row of cards */}
          <div className="bg-[#1a1a2e] rounded-xl p-3">
            <div className="text-xs text-[#888899] mb-2 text-center">
              Your hand ({myHand.length} cards)
              {!isMyTurn && <span className="ml-2 text-[#555566]">· Wait for your turn</span>}
            </div>
            <div className="flex gap-2 overflow-x-auto pb-1 justify-center flex-wrap">
              {myHand.map(card => {
                // A card is highlighted (green glow) only if it can legally be played
                const canPlay = isMyTurn && pile
                  ? isPlayable(card, currentColor, pile.kind, pendingDraw)
                  : false
                return (
                  <UnoCard
                    key={card.card_id}
                    card={card}
                    size="md"
                    playable={canPlay}
                    onClick={() => handleCardClick(card)}
                    className={!isMyTurn || !canPlay ? 'opacity-60' : ''}
                  />
                )
              })}
            </div>
          </div>

        </div>
      )}

      {/* ── ENDED STAGE — results overlay ───────────────────────────────── */}
      {stage === 'ended' && leaderboard && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-[#1a1a2e] border border-[#2a2a4a] rounded-2xl p-8 max-w-sm w-full text-center shadow-2xl">
            {/* Big trophy or cat crying depending on whether we won */}
            <div className="text-5xl mb-3">
              {leaderboard[0]?.player_id === myPlayerId ? '🏆' : '😿'}
            </div>
            <h2 className="text-2xl font-black text-white mb-1">
              {leaderboard[0]?.player_id === myPlayerId ? 'You Win!' : 'You Lose'}
            </h2>
            <p className="text-[#888899] text-sm mb-6">Final Scores</p>

            {/* Leaderboard — sorted by score, highest first */}
            <div className="flex flex-col gap-2 mb-6">
              {leaderboard.map((p, i) => {
                const medals = ['🥇', '🥈', '🥉', '4️⃣']
                return (
                  <div key={p.player_id} className="flex items-center justify-between bg-[#12121f] rounded-lg px-4 py-2">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{medals[i] ?? '·'}</span>
                      <span className="text-sm font-semibold text-white">{p.username}</span>
                      {p.player_id === myPlayerId && <span className="text-xs text-[#6c63ff]">(you)</span>}
                    </div>
                    <span className="text-sm font-bold text-[#6c63ff]">{p.score} pts</span>
                  </div>
                )
              })}
            </div>

            <Button size="lg" onClick={() => navigate('/home')} className="w-full">
              Back to Lobby
            </Button>
          </div>
        </div>
      )}

      {/* ── Wild colour picker dialog ────────────────────────────────────── */}
      {/* Shown as a modal overlay when the player clicks a Wild or Draw4 card */}
      {pendingWild && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-40 p-4">
          <div className="bg-[#1a1a2e] border border-[#2a2a4a] rounded-2xl p-6 max-w-xs w-full text-center shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-2">Choose a Colour</h3>
            <p className="text-xs text-[#888899] mb-5">Pick the next active colour</p>
            <div className="grid grid-cols-2 gap-3">
              {WILD_COLORS.map(c => (
                <button
                  key={c.color}
                  onClick={() => handleColorPick(c.color)}
                  className={`${c.bg} text-white font-bold py-4 rounded-xl text-sm transition-transform hover:scale-105 active:scale-95 shadow-lg`}
                >
                  {c.label}
                </button>
              ))}
            </div>
            {/* Cancel returns to the hand without playing anything */}
            <button
              onClick={() => setPendingWild(null)}
              className="mt-4 text-xs text-[#888899] hover:text-white transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

    </div>
  )
}
