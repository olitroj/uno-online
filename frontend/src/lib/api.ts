// lib/api.ts — ALL REST API CALLS TO THE BACKEND.
//
// Every function here corresponds to one API endpoint on the FastAPI server.
// They all use the shared apiFetch() helper so we don't repeat the same
// fetch() boilerplate (credentials, error handling, JSON parsing) everywhere.
//
// Why credentials: 'include'?
//   Our auth uses an HttpOnly cookie set by the server on login.
//   fetch() does NOT send cookies by default for cross-origin requests.
//   'include' forces the cookie to be sent with every request, which is how
//   the server knows who you are.
//
// API endpoints covered (satisfies the ≥9 endpoints requirement):
//   POST   /me            — register
//   POST   /me/token      — login
//   DELETE /me/token      — logout
//   DELETE /me            — delete account
//   GET    /me/info       — get own profile
//   PUT    /me            — update profile
//   GET    /me/games      — game history (paginated)
//   GET    /me/friends    — friends list (paginated + filtered)  ← filtering endpoint
//   GET    /me/friends/count — total filtered count (for pagination)
//   POST   /me/friends/:u — send friend request
//   PATCH  /me/friends/:u — accept / reject friend request
//   DELETE /me/friends/:u — remove friend

import type { AccountInfo, Friend, GameRecord } from '@/types'

// All API calls go through Vite's proxy: /api → http://localhost:8000
// This avoids CORS issues during development.
const BASE =
  import.meta.env.VITE_ENABLE_VITE_PROXY === 'true'
    ? '/api'
    : ''

function fallbackErrorMessage(status: number) {
  if (status === 400) return 'The request could not be completed. Please check your input and try again.'
  if (status === 401) return 'Please log in again.'
  if (status === 403) return 'You do not have permission to do that.'
  if (status === 404) return 'The requested item could not be found.'
  if (status === 409) return 'That conflicts with existing data.'
  return `Request failed with status ${status}.`
}

function validationErrorMessage(detail: unknown) {
  if (!Array.isArray(detail)) return null

  const messages = detail
    .map(item => {
      if (!item || typeof item !== 'object') return null
      const record = item as Record<string, unknown>
      return typeof record.msg === 'string' ? record.msg : null
    })
    .filter((message): message is string => Boolean(message))

  if (messages.length === 0) return null
  return `Please check your input: ${messages.join(', ')}.`
}

function isGenericErrorMessage(message: string) {
  const normalized = message.trim().toLowerCase()
  return normalized === 'bad request'
    || normalized === 'unauthorized'
    || normalized === 'forbidden'
    || normalized === 'not found'
    || normalized === 'internal server error'
}

async function errorMessageFromResponse(res: Response) {
  const fallback = fallbackErrorMessage(res.status)
  const text = await res.text().catch(() => '')
  if (!text) return res.statusText || fallback

  try {
    const data = JSON.parse(text) as unknown
    if (data && typeof data === 'object' && 'detail' in data) {
      const detail = (data as { detail: unknown }).detail
      if (typeof detail === 'string' && detail.trim()) {
        return isGenericErrorMessage(detail) ? fallback : detail
      }
      return validationErrorMessage(detail) ?? fallback
    }
  } catch {
    // Plain-text errors are fine to show directly.
  }

  return text || fallback
}

// ── Shared helper ─────────────────────────────────────────────────────────────

// Sends a fetch request and returns the parsed JSON body.
// Throws an Error with the server's error message if the response is not OK (2xx).
async function apiFetch(path: string, options?: RequestInit) {
  const res = await fetch(BASE + path, {
    credentials: 'include',  // send the auth cookie with every request
    ...options,
  })
  if (!res.ok) {
    throw new Error(await errorMessageFromResponse(res))
  }
  if (res.status === 204) return null   // 204 = success but no body to parse
  return res.json().catch(() => null)
}

// ── Auth ──────────────────────────────────────────────────────────────────────

// Creates a new account. Throws if the username is already taken.
export async function register(username: string, password: string) {
  const body = new URLSearchParams({ username, password })
  await apiFetch('/me', { method: 'POST', body })
}

// Logs in and sets an HttpOnly cookie in the browser.
// After this, all subsequent apiFetch() calls are authenticated.
export async function login(username: string, password: string) {
  const body = new URLSearchParams({ username, password })
  await apiFetch('/me/token', { method: 'POST', body })
}

// Clears the auth cookie — the user is now logged out.
export async function logout() {
  await apiFetch('/me/token', { method: 'DELETE' })
}

// Permanently deletes the logged-in user's account from the database.
export async function deleteAccount() {
  await apiFetch('/me', { method: 'DELETE' })
}

// ── Profile ───────────────────────────────────────────────────────────────────

// Returns the current user's profile: username, status, wins, losses, total_score.
export async function getMyInfo(): Promise<AccountInfo> {
  return apiFetch('/me/info')
}

// Updates one or more profile fields. Only the fields you include are changed.
// Example: updateMyInfo({ description: 'Hello!' }) leaves username/password alone.
export async function updateMyInfo(data: Partial<{ username: string; password: string; status: string; description: string }>) {
  await apiFetch('/me', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

// ── Game history ──────────────────────────────────────────────────────────────

// Returns up to 20 past games for the current user, ordered newest first.
// page=0 is the first page, page=1 is the next 20, etc.
export async function getMyGames(page = 0): Promise<GameRecord[]> {
  return apiFetch(`/me/games?page=${page}`)
}

// ── Friends ───────────────────────────────────────────────────────────────────

// Returns up to 20 friends/requests for the current user.
// search: filters by username (server uses ILIKE '%search%' so partial matches work)
// page:   which page of results (page 0 = first 20, page 1 = next 20, etc.)
export async function getFriends(page = 0, search = ''): Promise<Friend[]> {
  const params = new URLSearchParams({ page: String(page), search })
  return apiFetch(`/me/friends?${params}`)
}

// Returns the TOTAL count of friends matching the search filter (not just one page).
// Used by the frontend to calculate how many pagination pages to show.
// Example: if you have 45 friends matching the filter, totalFriendPages = ceil(45/20) = 3
export async function getFriendsCount(search = ''): Promise<number> {
  const params = new URLSearchParams({ search })
  const data = await apiFetch(`/me/friends/count?${params}`)
  return data.count as number
}

// Sends a friend request to another user by their username.
export async function sendFriendRequest(username: string) {
  await apiFetch(`/me/friends/${encodeURIComponent(username)}`, { method: 'POST' })
}

// Responds to an incoming friend request.
// action = 'accept' → they become a friend
// action = 'reject' → request is declined
export async function respondToFriend(username: string, action: 'accept' | 'reject') {
  const body = new URLSearchParams({ action })
  await apiFetch(`/me/friends/${encodeURIComponent(username)}`, { method: 'PATCH', body })
}

// Removes an accepted friend, or cancels a pending outgoing request.
export async function removeFriend(username: string) {
  await apiFetch(`/me/friends/${encodeURIComponent(username)}`, { method: 'DELETE' })
}

// ── Public Account Info ───────────────────────────────────────────────────

// Returns a friend's public profile info by username
export async function getAccountInfo(username: string): Promise<AccountInfo> {
  return apiFetch(`/account/info/${encodeURIComponent(username)}`)
}

// Returns a friend's game history by username
export async function getAccountGames(username: string, page = 0): Promise<GameRecord[]> {
  return apiFetch(`/account/games/${encodeURIComponent(username)}?page=${page}`)
}
