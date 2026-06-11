# Code Explanation — Cat UNO Frontend

This document explains every frontend file, every important function, and the key concepts behind the technology used. It is written to help group members understand the code well enough to explain any part of it.

---

## Table of Contents

1. [Concepts You Must Understand](#1-concepts-you-must-understand)
2. [main.tsx — Entry Point](#2-maintsx--entry-point)
3. [App.tsx — Router](#3-apptsx--router)
4. [types/index.ts — TypeScript Types](#4-typesindexts--typescript-types)
5. [lib/utils.ts — Class Helper](#5-libutilsts--class-helper)
6. [lib/api.ts — REST API Calls](#6-libapits--rest-api-calls)
7. [hooks/useGameSocket.ts — WebSocket & Game State](#7-hooksusegamesocketts--websocket--game-state)
8. [components/ui/Button.tsx](#8-componentsuibuttontsx)
9. [components/ui/Badge.tsx](#9-componentsuibadgetsx)
10. [components/ui/Card.tsx](#10-componentsuicardtsx)
11. [components/ui/Input.tsx](#11-componentsuiinputtsx)
12. [components/UnoCard.tsx — Playing Card](#12-componentsunoocard-tsx--playing-card)
13. [pages/AuthPage.tsx — Login & Register](#13-pagesauthpagetsx--login--register)
14. [pages/HomePage.tsx — Home](#14-pageshomepagetsx--home)
15. [pages/GamePage.tsx — Game Board](#15-pagesgamepagetsx--game-board)
16. [How the Teacher Requirements Are Met](#16-how-the-teacher-requirements-are-met)

---

## 1. Concepts You Must Understand

### React
React is a JavaScript library for building user interfaces. Instead of manually updating HTML elements (`document.getElementById(...).innerText = ...`), you describe *what the UI should look like* for any given data. React figures out what changed and updates the browser for you.

**Component** — a function that returns HTML-like code (JSX). Everything on screen is a component.

```tsx
function Greeting({ name }: { name: string }) {
  return <h1>Hello, {name}!</h1>
}
// Used as: <Greeting name="Alice" />
```

### State (`useState`)
State is data that belongs to a component. When state changes, React automatically re-renders the component to show the new data.

```tsx
const [count, setCount] = useState(0)
// count = 0 initially
// Calling setCount(1) makes React re-render with count = 1
```

### Effect (`useEffect`)
An effect runs code *after* the component renders — used for fetching data, opening WebSocket connections, etc.

```tsx
useEffect(() => {
  fetchUserProfile()   // runs after render
}, [userId])           // re-runs whenever userId changes

useEffect(() => {
  openWebSocket()      // runs only once on first render
}, [])                 // empty array = run once
```

### TypeScript
TypeScript adds types to JavaScript. A type describes exactly what shape a value must have. TypeScript shows errors *before you run the code*, preventing many bugs.

```ts
interface Card {
  card_id: number
  kind: string
  color: string
}
// If you write card.colour (wrong spelling), TypeScript catches it immediately.
```

### Tailwind CSS
Tailwind is a CSS framework where you style elements by adding short class names directly in your JSX — no separate CSS file needed.

```tsx
<div className="bg-red-500 text-white px-4 py-2 rounded-lg">
  Hello
</div>
// bg-red-500 = red background
// text-white = white text
// px-4 py-2 = horizontal/vertical padding
// rounded-lg = rounded corners
```

### WebSocket vs HTTP
- **HTTP**: browser sends a request → server answers → connection closes. Used for REST API calls.
- **WebSocket**: a persistent two-way connection. Once open, both sides can send messages at any time. Used for the game so the server can instantly push "your opponent played a card" to all players.

### HttpOnly Cookie (auth)
When you log in, the API server sets an HttpOnly cookie. This cookie:
- Is sent automatically with every request (you don't manage it in JavaScript)
- Cannot be read by JavaScript (prevents theft via XSS attacks)
- Is how the server identifies who you are on every API call and WebSocket connection

---

## 2. main.tsx — Entry Point

**What it does:** finds the `<div id="root">` in index.html and tells React to render the entire app inside it.

```tsx
createRoot(document.getElementById('root')!).render(<App />)
```

**Why StrictMode is removed:**  
React's StrictMode (a development tool) intentionally runs every `useEffect` *twice* — it mounts, unmounts, then mounts again. Our WebSocket hook opens a connection in `useEffect`. With StrictMode, two connections open at the same time and the server rejects the second with "already connected". Removing StrictMode prevents this.

---

## 3. App.tsx — Router

**What it does:** maps URL paths to page components. When the URL changes, a different page component is shown — without the browser reloading the page.

```tsx
<BrowserRouter>        // watches the address bar
  <Routes>             // picks the first matching Route
    <Route path="/"     element={<AuthPage />} />
    <Route path="/home" element={<HomePage />} />
    <Route path="/game" element={<GamePage />} />
    <Route path="*"     element={<Navigate to="/" replace />} />
  </Routes>
</BrowserRouter>
```

- `path="*"` — catches any unknown URL and redirects to `/`
- Navigation between pages uses `useNavigate()` inside pages: `navigate('/home')`

---

## 4. types/index.ts — TypeScript Types

**What it does:** defines the shape of every major data object in the app. These are used by TypeScript to catch mistakes at compile time.

| Type | Where it comes from | What it represents |
|------|--------------------|--------------------|
| `CardColor` | Game server | One of RED, GREEN, BLUE, YELLOW, NONE |
| `CardKind` | Game server | Card type: ZERO–NINE, SKIP, REVERSE, DRAW2, WILD, DRAW4 |
| `Card` | Game server | A single UNO card with card_id, kind, color |
| `Player` | Game server | A player in the live session (temporary player_id, username, score) |
| `AccountInfo` | API server GET /me/info | Full profile: username, status, wins, losses, total_score |
| `GameRecord` | API server GET /me/games | One game: start_time, end_time, score, win |
| `Friend` | API server GET /me/friends | A friend entry: username, status (pending/accepted/rejected) |
| `GameState` | Built client-side | Everything about the current game, built from WebSocket events |

**Important: `handSizes`**  
```ts
handSizes: Record<number, number>
// Maps player_id → how many cards they currently hold
// e.g. { 0: 7, 1: 5 }  means player 0 has 7 cards, player 1 has 5
```
We never see opponents' actual cards — only the count, updated from events.

---

## 5. lib/utils.ts — Class Helper

**What it does:** exports one function, `cn()`, that safely merges Tailwind class strings.

**The problem it solves:**  
If you write `className="px-4 px-6"`, both classes apply and the result is unpredictable. When you combine a base class string with an override from a prop, you can get duplicates or conflicts.

**How `cn()` works:**
1. `clsx()` flattens arrays, ignores `undefined`/`false` values
2. `twMerge()` removes Tailwind conflicts — it keeps only the *last* value for each CSS property

```ts
cn('px-4 py-2', isLarge && 'px-6')
// → 'py-2 px-6'   (px-4 removed because px-6 overrides it)
```

---

## 6. lib/api.ts — REST API Calls

**What it does:** wraps every REST API endpoint in a simple async function. All 12 functions use the shared `apiFetch()` helper.

### `apiFetch(path, options)` — the shared helper

```ts
async function apiFetch(path: string, options?: RequestInit) {
  const res = await fetch(BASE + path, {
    credentials: 'include',  // always send the auth cookie
    ...options,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText)
    throw new Error(text || `HTTP ${res.status}`)
  }
  if (res.status === 204) return null   // no body
  return res.json().catch(() => null)
}
```

- `credentials: 'include'` — tells the browser to send the HttpOnly cookie with every request. Without this, `fetch()` would not send cookies.
- If the server responds with an error (not 2xx), it reads the server's error message and throws it so the calling function can display it to the user.
- `204 No Content` — some endpoints (logout, delete) return no body, so we skip `res.json()`.

### The 12 functions

| Function | HTTP | Path | What it sends |
|----------|------|------|---------------|
| `register(u, p)` | POST | `/me` | form body: username, password |
| `login(u, p)` | POST | `/me/token` | form body: username, password |
| `logout()` | DELETE | `/me/token` | nothing |
| `deleteAccount()` | DELETE | `/me` | nothing |
| `getMyInfo()` | GET | `/me/info` | nothing |
| `updateMyInfo(data)` | PUT | `/me` | JSON body |
| `getMyGames(page)` | GET | `/me/games?page=N` | query param |
| `getFriends(page, search)` | GET | `/me/friends?page=N&search=Q` | query params |
| `getFriendsCount(search)` | GET | `/me/friends/count?search=Q` | query param |
| `sendFriendRequest(u)` | POST | `/me/friends/{u}` | nothing |
| `respondToFriend(u, action)` | PATCH | `/me/friends/{u}` | form body: action |
| `removeFriend(u)` | DELETE | `/me/friends/{u}` | nothing |

---

## 7. hooks/useGameSocket.ts — WebSocket & Game State

This is the most complex file. It handles the entire WebSocket connection and maintains all game state by processing server events one by one.

### Why a hook?

`GamePage.tsx` only needs to know: "what is the game state?" and "how do I play a card?". All the messy WebSocket code is hidden inside this hook and the page just calls it:

```ts
const { gameState, playCard, drawCards, startGame, error, connected } = useGameSocket()
```

### The state object (`GameState`)

The server never sends us the "full game state" in one message. We receive individual events and build the state incrementally:

| Field | Set by event |
|-------|-------------|
| `stage` | `GAME_START` → `'playing'`, `GAME_END` → `'ended'` |
| `myPlayerId` | `GAME_START` (from `hand.player_id`) |
| `myHand` | `GAME_START` (initial), `PLAY_CARD` (remove played card), `DRAW_CARDS` (add drawn cards) |
| `pile` | `GAME_START`, `PLAY_CARD` |
| `currentColor` | `GAME_START`, `PLAY_CARD` |
| `turn` | `GAME_START`, `PLAY_CARD`, `DRAW_CARDS`, `DREW_CARDS` |
| `pendingDraw` | `PLAY_CARD` (set), `DRAW_CARDS` / `DREW_CARDS` (reset to 0) |
| `players` | `LOBBY_STATE`, `PLAYER_JOIN`, `PLAYER_LEAVE`, `PLAY_CARD`, `DREW_CARDS` |
| `leaderboard` | `GAME_END` |
| `handSizes` | `GAME_START` (all set to 7), `PLAY_CARD` (−1 for opponent), `DREW_CARDS` (+N for opponent) |

### Key implementation details

**`myPlayerIdRef` vs state:**  
We store our own player_id in a `useRef` (not `useState`) because we need to read it inside `onmessage` event handlers. Event handlers are closures — they capture variables from when they were created. A `ref` always gives the current value, avoiding "stale closure" bugs.

**`didConnectRef` guard:**  
```ts
const didConnectRef = useRef(false)
useEffect(() => {
  if (didConnectRef.current) return   // skip the second mount
  didConnectRef.current = true
  const ws = new WebSocket('/ws')
  ...
  ws.onclose = () => { ...; didConnectRef.current = false }
}, [])
```
Without this, React's development mode would open two WebSocket connections.

**`useCallback`:**  
`playCard`, `drawCards`, and `startGame` are wrapped in `useCallback`. This keeps the function reference stable across re-renders (the same function object), which is important for performance and correctness when passing them as props.

### Event handling flow

```
Server sends JSON → ws.onmessage → handleServerEvent(msg)
  → checks msg.eventType
  → calls setGameState(s => { ...s, [relevant fields updated] })
  → React re-renders GamePage with new data
```

### Action functions

```ts
// Play a card: send card_id and optionally a chosen colour (for Wild/Draw4)
const playCard = useCallback((cardId: number, newColor: CardColor = 'NONE') => {
  wsRef.current?.send(JSON.stringify({
    eventType: 'PLAY_CARD', messageType: 'REQUEST',
    details: { card_id: cardId, new_color: newColor },
  }))
}, [])
```

The `?.` operator means "only call `.send()` if `wsRef.current` is not null" — safe even if the socket closed.

---

## 8. components/ui/Button.tsx

A reusable button with **variant** (colour style) and **size** props.

```tsx
<Button variant="danger" size="sm" onClick={handleDelete}>Delete</Button>
```

**Variants:**
- `primary` — purple (main actions)
- `secondary` — dark grey (secondary actions)
- `danger` — red (destructive: delete account)
- `ghost` — transparent (logout, cancel, back)

**Sizes:** `sm`, `md` (default), `lg`

The `...props` spread passes any HTML button attribute (onClick, disabled, type, etc.) through without listing them explicitly. `cn()` merges the base classes, variant classes, size classes, and any extra `className` prop.

---

## 9. components/ui/Badge.tsx

A small coloured pill label. Used for:
- Player status: `● online` (green), `● in game` (yellow), `● offline` (grey)
- Friend status: `Friends` (green), `Pending` (yellow), `Rejected` (red)
- Game result: `Win` (green), `Loss` (red)

**Variants:** `default` (grey), `success` (green), `warning` (orange), `danger` (red), `info` (blue)

---

## 10. components/ui/Card.tsx

A dark rounded box container — used for grouping content on the home page (profile section, each friend entry, each game history row). Not to be confused with the UNO playing card.

Exports `Card` (the container) and `CardTitle` (a styled `<h2>` heading inside a card).

---

## 11. components/ui/Input.tsx

A styled text input with an optional label above and an optional error message below.

```tsx
<Input
  id="username"
  name="username"
  label="Username"
  required
  minLength={3}
  maxLength={32}
  pattern="[A-Za-z0-9_]+"
  error={errorMessage}    // turns the border red and shows the message
/>
```

**HTML validation attributes (teacher requirement — layer 1):**
- `required` — browser blocks form submission if the field is empty
- `minLength` — browser blocks if fewer characters than the minimum
- `maxLength` — browser stops the user typing past the limit
- `pattern` — browser validates the value against a regex
- `type="password"` — browser hides characters with dots

The `error` prop: if provided, the border turns red and the error message appears below the input.

---

## 12. components/UnoCard.tsx — Playing Card

Exports three components: `UnoCard`, `CardBack`, `CardSlot`.

### UnoCard — face-up card

Visual structure:
```
┌──────────────┐
│ +2           │  ← top-left corner label (from cornerLabel())
│   ╔══════╗   │
│   ║  🐾  ║   │  ← white oval (-12° tilt) with cat emoji (from catEmoji())
│   ╚══════╝   │
│          +2  │  ← bottom-right label, rotated 180°
└──────────────┘
```

**`cornerLabel(card)`** — returns the text shown in both corners:
```ts
{ ZERO: '0', ONE: '1', ..., SKIP: '⊘', REVERSE: '↺', DRAW2: '+2', WILD: '★', DRAW4: '+4' }
```

**`catEmoji(card)`** — each card kind gets its own unique cat face so cards are distinguishable at a glance (also helps colourblind players).

**Wild card overlay:** when `card.color === 'NONE'` (Wild or Draw4), a four-coloured quadrant grid is layered on top of the card background.

**`displayColor` prop:** after a Wild card is played, the active colour changes but the card object's `color` field stays `'NONE'`. The `displayColor` prop overrides the background colour to show the chosen colour. This is how the discard pile shows "WILD played as RED" with a red background.

**`playable` prop:** adds a green glow CSS class (`card-playable`, defined in `index.css`) to highlight cards the player can legally play.

### CardBack — face-down card
Shows a dark card with "UNO" text. Used for:
- The draw pile (clickable on your turn)
- Opponents' hands (we know the count but not the actual cards)

### CardSlot — empty placeholder
A dashed box shown when the discard pile is empty (before the game starts).

---

## 13. pages/AuthPage.tsx — Login & Register

**Stages:** one page, two tabs (`'login'` or `'register'`), controlled by the `tab` state.

### Form validation — two layers (teacher requirement)

**Layer 1 — HTML attributes** on the `<Input>` elements:
```tsx
<Input required minLength={3} maxLength={32} pattern="[A-Za-z0-9_]+" />
```
The browser enforces these before the form's `onSubmit` even fires. The user sees the browser's native tooltip if they violate them.

**Layer 2 — JavaScript** in `validateRegister()`:
```ts
function validateRegister(username, password, confirm): string {
  if (username.length < 3) return 'Username must be at least 3 characters.'
  if (password.length < 6) return 'Password must be at least 6 characters.'
  if (password !== confirm) return 'Passwords do not match.'
  return ''  // empty string = no error
}
```
This catches things HTML cannot — like checking that two fields match. If it returns an error string, the form shows it and stops. If it returns `''`, the API call proceeds.

### Flow

**Login:**
1. `handleLogin()` is called when the form submits
2. `e.preventDefault()` stops the browser from doing a full page reload
3. It reads the field values from the form DOM using `form.elements.namedItem('username')`
4. Calls `login()` from api.ts → `POST /me/token`
5. On success: `navigate('/home')`
6. On failure: shows the server's error message

**Register:**
1. Same as login, but calls `validateRegister()` first
2. If valid: `register()` → `POST /me`, then immediately `login()` → `POST /me/token`

### `loading` state
While an API call is in flight, `loading` is set to `true`. This disables the submit button so the user can't double-submit. The `finally` block always resets it to `false`.

---

## 14. pages/HomePage.tsx — Home

The main hub after login. Has a profile card and two tabs (Friends / Game History).

### State variables

```ts
// Profile
const [profile, setProfile]     = useState<AccountInfo | null>(null)
const [editMode, setEditMode]   = useState(false)      // show description input
const [editDesc, setEditDesc]   = useState('')

// Friends
const [friends, setFriends]         = useState<Friend[]>([])
const [friendSearch, setFriendSearch] = useState('')   // search box text
const [friendPage, setFriendPage]   = useState(0)      // current page (0-indexed)
const [friendTotal, setFriendTotal] = useState(0)      // total matching count

// Games
const [games, setGames]       = useState<GameRecord[]>([])
const [gamePage, setGamePage] = useState(0)
const [hasMoreGames, setHasMoreGames] = useState(false)
```

### Pagination + Filtering — how they work together (teacher requirement)

```ts
const loadFriends = useCallback(async () => {
  const [list, count] = await Promise.all([
    getFriends(friendPage, friendSearch),   // GET /me/friends?page=N&search=Q
    getFriendsCount(friendSearch),          // GET /me/friends/count?search=Q
  ])
  setFriends(list)
  setFriendTotal(count)
}, [friendPage, friendSearch])
```

`Promise.all` runs both API calls at the same time (parallel), then waits for both. This is faster than calling them one after another.

```ts
const totalFriendPages = Math.ceil(friendTotal / PAGE_SIZE)
```

`Math.ceil` rounds up: 21 friends / 20 per page = 2 pages (not 1.05).  
If a search filter reduces the count from 45 to 3, `totalFriendPages` drops from 3 to 1 automatically — the Prev/Next buttons reflect this immediately.

```ts
useEffect(() => { setFriendPage(0) }, [friendSearch])
```

Whenever the search text changes, reset to page 0. Without this, you could be on page 3, type a search with only 1 page of results, and see an empty page 3.

### `useCallback` — why it's needed

```ts
const loadFriends = useCallback(async () => { ... }, [friendPage, friendSearch])
useEffect(() => { loadFriends() }, [loadFriends])
```

Without `useCallback`, every render would create a new `loadFriends` function object. The `useEffect` would see "the dependency `loadFriends` changed" and run again — causing another render, which creates another function, which triggers the effect again. **Infinite loop.** `useCallback` memoises the function so it only changes when its listed dependencies (`friendPage`, `friendSearch`) change.

### Handlers

| Handler | What it does |
|---------|-------------|
| `handleLogout()` | Calls `logout()` → navigates to `/` |
| `handleSaveDesc()` | Calls `updateMyInfo({ description })` → updates local profile state |
| `handleDeleteAccount()` | Shows a `confirm()` dialog → calls `deleteAccount()` → navigates to `/` |
| `handleAddFriend(e)` | Prevents default form submit → calls `sendFriendRequest()` → reloads friends |
| `handleRespond(u, action)` | Calls `respondToFriend()` (accept/reject) → reloads friends |
| `handleRemoveFriend(u)` | Shows `confirm()` → calls `removeFriend()` → reloads friends |

---

## 15. pages/GamePage.tsx — Game Board

Has three visual stages based on `gameState.stage`.

### `isPlayable(card, pileColor, pileKind, pendingDraw)` — client-side rule check

```ts
function isPlayable(card, pileColor, pileKind, pendingDraw): boolean {
  if (pendingDraw > 0) return false               // must draw the penalty first
  if (card.kind === 'WILD' || card.kind === 'DRAW4') return true  // always playable
  if (card.color === pileColor) return true        // same colour
  if (card.kind === pileKind) return true          // same number or action type
  return false
}
```

This mirrors the server's `is_playable()` in `event_handler.py`. We check it on the client so we can:
1. Add a green glow to playable cards (visual feedback)
2. Block click events on unplayable cards without a network round-trip

The server still enforces the real rules — a malicious client can't trick it.

### Wild card flow

1. Player clicks a Wild or Draw4 → `handleCardClick()` runs
2. Since it's a Wild, `setPendingWild(card)` — stores the card in state
3. The colour picker dialog renders (because `pendingWild !== null`)
4. Player clicks a colour → `handleColorPick(color)` runs
5. `playCard(pendingWild.card_id, color)` sends the event to the server
6. `setPendingWild(null)` — closes the dialog

### Stage: `'waiting'` — lobby

Shows who is in the lobby and a **Start Game** button when `players.length >= 2`.

Any player can click Start Game — the server verifies the player count.

### Stage: `'playing'` — game board

Three sections:
1. **Opponents area** — one panel per opponent showing face-down card stack and "Thinking…" if it's their turn
2. **Centre** — draw pile (clickable on your turn), discard pile (top card), turn indicator
3. **Your hand** — all your cards; playable ones glow green

**`pendingDraw > 0`:** shown as "Draw +2!" or "Draw +4!" warning. The draw pile glows. Playing any card is blocked until you draw.

**UNO badge:** shown when `myHand.length === 1 && isMyTurn`.

### Stage: `'ended'` — results

Full-screen overlay with medals (🥇🥈🥉4️⃣), player scores, and a "Back to Lobby" button.

---

## 16. How the Teacher Requirements Are Met

### Form validation

| Where | Type | What it checks |
|-------|------|----------------|
| `AuthPage.tsx` `<Input required minLength={3} maxLength={32} pattern="[A-Za-z0-9_]+"` | HTML attr | Username not empty, length 3–32, valid characters |
| `AuthPage.tsx` `<Input type="password" required minLength={6}` | HTML attr | Password not empty, ≥6 characters |
| `AuthPage.tsx` `validateRegister()` | JavaScript | Passwords match |
| `HomePage.tsx` Add Friend form | HTML attr | `required minLength={3} maxLength={32}` |

### Pagination + Filtering

- `GET /me/friends?page=N&search=Q` — server filters with `ILIKE '%Q%'`
- `GET /me/friends/count?search=Q` — returns the total count for the current filter
- `totalFriendPages = Math.ceil(count / 20)` — shrinks when filter narrows results
- `useEffect(() => { setFriendPage(0) }, [friendSearch])` — reset to page 1 on new search

### 9+ API Endpoints

12 endpoints (see lib/api.ts section above).

### Responsiveness

Tailwind responsive class examples in the code:
- `flex-col sm:flex-row` — column on mobile, row on tablet/desktop
- `hidden sm:block` — hide username in nav bar on small screens
- `max-w-4xl mx-auto` — centre content with max width on wide screens
- `flex-wrap` and `overflow-x-auto` — card hand wraps or scrolls on narrow screens

### Intuitive Navigation

- Top bar on every page (logo, username, logout / back button)
- Connection dot: green = game server connected, red = disconnected
- Playable cards: green glow. Unplayable cards: 60% opacity
- "Your turn!" / "Opponent's turn" text
- "Draw +2!" / "Draw +4!" warning when penalty is pending
- "UNO! 🃏" badge when player has 1 card left
- Lobby shows player count and "Start Game (N/4)" button
