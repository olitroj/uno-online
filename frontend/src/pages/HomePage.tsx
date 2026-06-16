// pages/HomePage.tsx — Home page (route: "/home")
//
// Three sections: profile card, friends tab, game history tab.
//
// Friends list supports search + pagination together:
//   - Search filters by username (?search=...) and resets to page 0 on change
//   - Total page count comes from getFriendsCount() so it shrinks when search narrows results

import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardTitle } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import {
  deleteAccount,
  getAccountGames,
  getAccountInfo,
  getFriends, getFriendsCount,
  getMyGames,
  getMyInfo,
  logout,
  removeFriend,
  respondToFriend,
  sendFriendRequest,
  updateMyInfo,
} from '@/lib/api'
import type { AccountInfo, Friend, GameRecord } from '@/types'
import { CheckCircle, ChevronLeft, ChevronRight, LogOut, Play, Trash2, Trophy, UserPlus, XCircle } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

// How many friends to show per page
const PAGE_SIZE = 20

export default function HomePage() {
  const navigate = useNavigate()

  // ── Profile state ──────────────────────────────────────────────────────────
  const [profile, setProfile]       = useState<AccountInfo | null>(null)   // null = still loading
  const [editMode, setEditMode]     = useState(false)                       // true = edit form visible
  const [editUsername, setEditUsername] = useState('')                      // current value of username input
  const [editPassword, setEditPassword] = useState('')                      // current value of password input
  const [editDesc, setEditDesc]     = useState('')                          // current value of description input
  const [profileMsg, setProfileMsg] = useState('')                          // success/error message below profile

  // ── Friends state ──────────────────────────────────────────────────────────
  const [friends, setFriends]           = useState<Friend[]>([])
  const [friendSearch, setFriendSearch] = useState('')        // current text in the search box
  const [friendPage, setFriendPage]     = useState(0)         // current page index (0-based)
  const [friendTotal, setFriendTotal]   = useState(0)         // total matching friends (from count endpoint)
  const [addName, setAddName]           = useState('')         // value of the "Add Friend" input
  const [friendMsg, setFriendMsg]       = useState('')         // status message below friend add form
  const [selectedFriend, setSelectedFriend] = useState<string | null>(null)
  const [friendProfile, setFriendProfile] = useState<AccountInfo | null>(null)
  const [friendGames, setFriendGames] = useState<GameRecord[]>([])
  const [friendGamePage, setFriendGamePage] = useState(0)
  const [friendHasMoreGames, setFriendHasMoreGames] = useState(false)
  const [friendProfileMsg, setFriendProfileMsg] = useState('')
  const [friendProfileLoading, setFriendProfileLoading] = useState(false)

  // ── Game history state ─────────────────────────────────────────────────────
  const [games, setGames]               = useState<GameRecord[]>([])
  const [gamePage, setGamePage]         = useState(0)
  const [hasMoreGames, setHasMoreGames] = useState(false)     // true if there might be a next page

  // ── Active tab ─────────────────────────────────────────────────────────────
  const [tab, setTab] = useState<'friends' | 'history'>('friends')

  // ── Load profile once on mount ─────────────────────────────────────────────
  // If getMyInfo() fails (e.g. not logged in), redirect to login page.
  useEffect(() => {
    getMyInfo().then(info => {
      setProfile(info)
      setEditUsername(info.username)
      setEditPassword('')
      setEditDesc(info.description ?? '')
    }).catch(() => navigate('/'))
  }, [navigate])

  // useCallback prevents an infinite loop: without it, a new function object is created
  // every render, making useEffect think its dependency changed and re-running endlessly.
  const loadFriends = useCallback(async () => {
    try {
      // Run both API calls at the same time (parallel) with Promise.all
      const [list, count] = await Promise.all([
        getFriends(friendPage, friendSearch),       // the current page of results
        getFriendsCount(friendSearch),              // total count for pagination math
      ])
      setFriends(list)
      setFriendTotal(count)
    } catch {
      setFriendMsg('Failed to load friends')
    }
  }, [friendPage, friendSearch])

  useEffect(() => { loadFriends() }, [loadFriends])

  // Reset to page 0 whenever search changes so you don't land on an empty page.
  useEffect(() => { setFriendPage(0) }, [friendSearch])

  // ── Reload game history whenever page changes ──────────────────────────────
  const loadGames = useCallback(async () => {
    try {
      const list = await getMyGames(gamePage)
      setGames(list)
      // If we got a full page, there's probably a next page
      setHasMoreGames(list.length === PAGE_SIZE)
    } catch {
      /* ignore — history failure doesn't break the page */
    }
  }, [gamePage])

  useEffect(() => { loadGames() }, [loadGames])

  const loadFriendProfile = useCallback(async () => {
    if (!selectedFriend) return
    setFriendProfileLoading(true)
    setFriendProfileMsg('')
    try {
      const [info, list] = await Promise.all([
        getAccountInfo(selectedFriend),
        getAccountGames(selectedFriend, friendGamePage),
      ])
      setFriendProfile(info)
      setFriendGames(list)
      setFriendHasMoreGames(list.length === PAGE_SIZE)
    } catch (err) {
      setFriendProfile(null)
      setFriendGames([])
      setFriendHasMoreGames(false)
      setFriendProfileMsg(err instanceof Error ? err.message : 'Failed to load friend profile')
    } finally {
      setFriendProfileLoading(false)
    }
  }, [selectedFriend, friendGamePage])

  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { loadFriendProfile() }, [loadFriendProfile])

  // ── Action handlers ────────────────────────────────────────────────────────

  // Logs out and sends the user back to the login page
  async function handleLogout() {
    await logout()
    navigate('/')
  }

  // Saves the edited profile fields to the server and updates local profile state
  async function handleSaveProfile() {
    try {
      const updates: Parameters<typeof updateMyInfo>[0] = {}
      if (editUsername !== profile?.username) updates.username = editUsername
      if (editPassword) updates.password = editPassword
      if (editDesc !== (profile?.description ?? '')) updates.description = editDesc

      if (Object.keys(updates).length === 0) {
        setEditMode(false)
        return
      }

      await updateMyInfo(updates)
      setProfile(p => p ? { ...p, username: editUsername, description: editDesc } : p)
      setEditMode(false)
      setEditPassword('')
      setProfileMsg('Profile updated!')
      setTimeout(() => setProfileMsg(''), 2500)
    } catch (err) {
      setProfileMsg(err instanceof Error ? err.message : 'Update failed')
    }
  }

  // Shows a confirmation dialog before permanently deleting the account
  async function handleDeleteAccount() {
    if (!confirm('Delete your account? This cannot be undone.')) return
    await deleteAccount()
    navigate('/')
  }

  // Sends a friend request by username
  async function handleAddFriend(e: React.FormEvent) {
    e.preventDefault()
    if (!addName.trim()) return
    setFriendMsg('')
    try {
      await sendFriendRequest(addName.trim())
      setAddName('')
      setFriendMsg(`Friend request sent to "${addName.trim()}"`)
      loadFriends()  // refresh the list to show the pending entry
    } catch (err) {
      setFriendMsg(err instanceof Error ? err.message : 'Failed to send request')
    }
    setTimeout(() => setFriendMsg(''), 3000)
  }

  // Accepts or rejects an incoming friend request
  async function handleRespond(username: string, action: 'accept' | 'reject') {
    try {
      await respondToFriend(username, action)
      loadFriends()
    } catch (err) {
      setFriendMsg(err instanceof Error ? err.message : 'Failed')
    }
  }

  // Removes an accepted friend (with confirmation)
  async function handleRemoveFriend(username: string) {
    if (!confirm(`Remove ${username} from friends?`)) return
    try {
      await removeFriend(username)
      if (selectedFriend === username) {
        clearSelectedFriend()
      }
      loadFriends()
    } catch (err) {
      setFriendMsg(err instanceof Error ? err.message : 'Failed')
    }
  }

  function clearSelectedFriend() {
    setSelectedFriend(null)
    setFriendProfile(null)
    setFriendGames([])
    setFriendGamePage(0)
    setFriendProfileMsg('')
    setFriendHasMoreGames(false)
  }

  function handleSelectFriend(friend: Friend) {
    if (friend.status !== 'accepted') return
    if (selectedFriend === friend.username) {
      clearSelectedFriend()
      return
    }
    if (selectedFriend !== friend.username) {
      setFriendProfile(null)
      setFriendGames([])
      setFriendProfileMsg('')
    }
    setSelectedFriend(friend.username)
    setFriendGamePage(0)
  }

  // ── Derived values ─────────────────────────────────────────────────────────

  const totalFriendPages = Math.ceil(friendTotal / PAGE_SIZE)

  // ── Badge helpers ──────────────────────────────────────────────────────────

  // Returns a coloured <Badge> matching the player's online status
  function statusBadge(s: string) {
    if (s === 'online')  return <Badge variant="success">● online</Badge>
    return <Badge variant="default">● offline</Badge>
  }

  function gameHistoryCard(g: GameRecord, i: number) {
    return (
      <Card key={`${g.start_time}-${i}`} className="flex items-center gap-4 py-3">
        <div className={`flex-shrink-0 text-2xl ${g.win ? 'text-[#f0a030]' : 'text-[#555566]'}`}>
          {g.win ? <Trophy size={24} /> : '💀'}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-semibold text-white">
            {g.win ? 'Victory' : 'Defeat'}
          </div>
          <div className="text-xs text-[#888899]">
            {new Date(g.start_time).toLocaleDateString()} · Score: {g.score}
          </div>
        </div>
        <Badge variant={g.win ? 'success' : 'danger'}>
          {g.win ? 'Win' : 'Loss'}
        </Badge>
      </Card>
    )
  }

  // Returns a coloured <Badge> for a friend relationship status
  function friendStatusBadge(s: Friend['status']) {
    if (s === 'accepted') return <Badge variant="success">Friends</Badge>
    if (s === 'pending')  return <Badge variant="warning">Pending</Badge>
    return <Badge variant="danger">Rejected</Badge>
  }

  // ── Loading state ──────────────────────────────────────────────────────────

  // Show a spinner until the profile API call returns
  if (!profile) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-[#888899]">Loading…</div>
      </div>
    )
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-[#0f0f13]">

      {/* ── Navigation bar — fixed at top ───────────────────────────────── */}
      <header className="border-b border-[#2a2a4a] bg-[#12121f] px-4 py-3">
        <div className="mx-auto max-w-4xl flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🐱</span>
            <span className="font-black text-white text-lg">Cat UNO</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-[#888899] hidden sm:block">{profile.username}</span>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut size={14} /> Logout
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-6 flex flex-col gap-6">

        {/* ── Play Game button ─────────────────────────────────────────── */}
        <div className="flex justify-center">
          <Button
            size="lg"
            onClick={() => navigate('/game')}
            className="gap-3 px-10 py-4 text-lg rounded-2xl shadow-lg shadow-[#6c63ff]/20"
          >
            <Play size={22} fill="white" /> Play Game
          </Button>
        </div>

        {/* ── Profile card ─────────────────────────────────────────────── */}
        <Card>
          {/* flex-col on mobile, flex-row on sm+ screens (responsive) */}
          <div className="flex flex-col sm:flex-row sm:items-start gap-4">

            {/* Cat avatar */}
            <div className="flex-shrink-0 w-16 h-16 rounded-full bg-[#2a2a4a] flex items-center justify-center text-3xl">
              🐱
            </div>

            {/* Username + status + description */}
            <div className="flex-1 min-w-0">
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <span className="text-lg font-bold text-white">{profile.username}</span>
              </div>

              {/* Toggle between view mode and edit mode for profile */}
              {editMode ? (
                <div className="flex flex-col gap-3 mt-3">
                  <div>
                    <label className="text-xs text-[#888899] block mb-1">Username</label>
                    <Input
                      value={editUsername}
                      onChange={e => setEditUsername(e.target.value)}
                      placeholder="Username"
                      minLength={3}
                      maxLength={32}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-[#888899] block mb-1">Password (leave blank to keep current)</label>
                    <Input
                      type="password"
                      value={editPassword}
                      onChange={e => setEditPassword(e.target.value)}
                      placeholder="New password"
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-[#888899] block mb-1">Description</label>
                    <Input
                      value={editDesc}
                      onChange={e => setEditDesc(e.target.value)}
                      placeholder="Add a description…"
                      maxLength={100}
                      className="w-full"
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" onClick={handleSaveProfile}>Save</Button>
                    <Button size="sm" variant="ghost" onClick={() => setEditMode(false)}>Cancel</Button>
                  </div>
                </div>
              ) : (
                <div>
                  <p
                    className="text-sm text-[#888899] cursor-pointer hover:text-[#e8e8f0] transition-colors mt-1"
                    onClick={() => setEditMode(true)}
                  >
                    {profile.description || <span className="italic">Click to add a description…</span>}
                  </p>
                  <button
                    onClick={() => setEditMode(true)}
                    className="text-xs text-[#6c63ff] hover:text-[#8875ff] transition-colors mt-2"
                  >
                    Edit profile
                  </button>
                </div>
              )}
              {profileMsg && <p className="text-xs text-[#55c48a] mt-1">{profileMsg}</p>}
            </div>

            {/* Win / Loss / Score stats */}
            <div className="flex gap-4 sm:gap-6 text-center flex-shrink-0">
              {[
                { label: 'Wins',   value: profile.wins,        color: 'text-[#55c48a]' },
                { label: 'Losses', value: profile.losses,      color: 'text-[#e05555]' },
                { label: 'Score',  value: profile.total_score, color: 'text-[#6c63ff]' },
              ].map(s => (
                <div key={s.label}>
                  <div className={`text-xl font-bold ${s.color}`}>{s.value}</div>
                  <div className="text-xs text-[#888899]">{s.label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Delete account — bottom of profile card */}
          <div className="mt-4 pt-4 border-t border-[#2a2a4a] flex justify-end">
            <Button variant="ghost" size="sm" onClick={handleDeleteAccount} className="text-[#e05555] hover:bg-[#3a1a1a]">
              <Trash2 size={13} /> Delete Account
            </Button>
          </div>
        </Card>

        {/* ── Tab switcher ─────────────────────────────────────────────── */}
        <div className="flex gap-1 bg-[#1a1a2e] rounded-lg p-1 w-fit">
          {(['friends', 'history'] as const).map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-5 py-1.5 rounded-md text-sm font-semibold capitalize transition-all ${
                tab === t ? 'bg-[#6c63ff] text-white' : 'text-[#888899] hover:text-white'
              }`}
            >
              {t === 'friends' ? '👥 Friends' : '🏆 History'}
            </button>
          ))}
        </div>

        {/* ── Friends tab ──────────────────────────────────────────────── */}
        {tab === 'friends' && (
          <div className="flex flex-col gap-4">

            {/* Add friend form */}
            <Card>
              <CardTitle>Add Friend</CardTitle>
              <form onSubmit={handleAddFriend} className="flex gap-2">
                <Input
                  value={addName}
                  onChange={e => setAddName(e.target.value)}
                  placeholder="Enter username"
                  minLength={3}
                  maxLength={32}
                  required
                  className="flex-1"
                />
                <Button type="submit">
                  <UserPlus size={15} /> Add
                </Button>
              </form>
              {friendMsg && (
                <p className={`text-xs mt-2 ${friendMsg.includes('sent') ? 'text-[#55c48a]' : 'text-[#e05555]'}`}>
                  {friendMsg}
                </p>
              )}
            </Card>

            {/* Search box — typing here updates friendSearch state → triggers loadFriends */}
            <div className="flex flex-col sm:flex-row gap-2 items-start sm:items-center">
              <Input
                value={friendSearch}
                onChange={e => setFriendSearch(e.target.value)}
                placeholder="🔍 Search friends by username…"
                className="flex-1"
              />
              {/* Shows total count so the user knows how many results exist */}
              <div className="text-sm text-[#888899] whitespace-nowrap">
                {friendTotal} result{friendTotal !== 1 ? 's' : ''}
              </div>
            </div>

            {/* Friends list */}
            {friends.length === 0 ? (
              <div className="text-center text-[#555566] py-8">
                {friendSearch ? 'No friends match your search.' : 'No friends yet. Add someone!'}
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                {friends.map(f => (
                  <Card
                    key={f.username}
                    role={f.status === 'accepted' ? 'button' : undefined}
                    tabIndex={f.status === 'accepted' ? 0 : undefined}
                    onClick={() => handleSelectFriend(f)}
                    onKeyDown={e => {
                      if (f.status === 'accepted' && (e.key === 'Enter' || e.key === ' ')) {
                        e.preventDefault()
                        handleSelectFriend(f)
                      }
                    }}
                    className={`flex items-center gap-3 py-3 transition-colors ${
                      f.status === 'accepted'
                        ? selectedFriend === f.username
                          ? 'border-[#6c63ff] bg-[#20203a] cursor-pointer'
                          : 'cursor-pointer hover:bg-[#20203a]'
                        : ''
                    }`}
                  >
                    <div className="w-9 h-9 rounded-full bg-[#2a2a4a] flex items-center justify-center text-lg flex-shrink-0">
                      🐱
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="font-semibold text-sm text-white truncate block">{f.username}</span>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {friendStatusBadge(f.status)}
                      {/* Show accept/reject buttons for pending requests */}
                      {f.status === 'pending' && (
                        <>
                          <button onClick={e => { e.stopPropagation(); handleRespond(f.username, 'accept') }} title="Accept" className="text-[#55c48a] hover:opacity-70 transition-opacity">
                            <CheckCircle size={18} />
                          </button>
                          <button onClick={e => { e.stopPropagation(); handleRespond(f.username, 'reject') }} title="Reject" className="text-[#e05555] hover:opacity-70 transition-opacity">
                            <XCircle size={18} />
                          </button>
                        </>
                      )}
                      {/* Show remove button for accepted friends */}
                      {f.status !== 'pending' && (
                        <button onClick={e => { e.stopPropagation(); handleRemoveFriend(f.username) }} title="Remove" className="text-[#555566] hover:text-[#e05555] transition-colors">
                          <XCircle size={18} />
                        </button>
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            )}

            {/* Pagination — only shown when there is more than one page of results.
                When search narrows results below PAGE_SIZE, this disappears automatically. */}
            {totalFriendPages > 1 && (
              <div className="flex items-center justify-center gap-3">
                <Button
                  variant="secondary" size="sm"
                  disabled={friendPage === 0}                     // can't go before page 0
                  onClick={() => setFriendPage(p => p - 1)}
                >
                  <ChevronLeft size={14} /> Prev
                </Button>
                <span className="text-sm text-[#888899]">
                  Page {friendPage + 1} / {totalFriendPages}
                </span>
                <Button
                  variant="secondary" size="sm"
                  disabled={friendPage >= totalFriendPages - 1}   // can't go past last page
                  onClick={() => setFriendPage(p => p + 1)}
                >
                  Next <ChevronRight size={14} />
                </Button>
              </div>
            )}

            {selectedFriend && (
              <Card>
                <CardTitle>Friend Profile</CardTitle>

                {friendProfileLoading && !friendProfile ? (
                  <div className="text-sm text-[#888899]">Loading...</div>
                ) : friendProfileMsg ? (
                  <div className="text-sm text-[#e05555]">{friendProfileMsg}</div>
                ) : friendProfile && (
                  <div className="flex flex-col gap-4">
                    <div className="flex flex-col sm:flex-row sm:items-start gap-4">
                      <div className="flex-shrink-0 w-16 h-16 rounded-full bg-[#2a2a4a] flex items-center justify-center text-3xl">
                        🐱
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-2 mb-1">
                          <span className="text-lg font-bold text-white">{friendProfile.username}</span>
                          {statusBadge(friendProfile.status)}
                        </div>
                        <p className="text-sm text-[#888899] mt-1">
                          {friendProfile.description || <span className="italic">No description yet.</span>}
                        </p>
                      </div>
                      <div className="flex gap-4 sm:gap-6 text-center flex-shrink-0">
                        {[
                          { label: 'Wins',   value: friendProfile.wins,        color: 'text-[#55c48a]' },
                          { label: 'Losses', value: friendProfile.losses,      color: 'text-[#e05555]' },
                          { label: 'Score',  value: friendProfile.total_score, color: 'text-[#6c63ff]' },
                        ].map(s => (
                          <div key={s.label}>
                            <div className={`text-xl font-bold ${s.color}`}>{s.value}</div>
                            <div className="text-xs text-[#888899]">{s.label}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="border-t border-[#2a2a4a] pt-4">
                      <div className="text-sm font-semibold text-[#e8e8f0] mb-3">Game History</div>
                      <div className="flex flex-col gap-2">
                        {friendGames.length === 0 ? (
                          <div className="text-center text-[#555566] py-6">No games played yet.</div>
                        ) : (
                          friendGames.map(gameHistoryCard)
                        )}
                      </div>

                      {(friendGamePage > 0 || friendHasMoreGames) && (
                        <div className="flex items-center justify-center gap-3 mt-4">
                          <Button
                            variant="secondary" size="sm"
                            disabled={friendGamePage === 0}
                            onClick={() => setFriendGamePage(p => p - 1)}
                          >
                            <ChevronLeft size={14} /> Prev
                          </Button>
                          <span className="text-sm text-[#888899]">Page {friendGamePage + 1}</span>
                          <Button
                            variant="secondary" size="sm"
                            disabled={!friendHasMoreGames}
                            onClick={() => setFriendGamePage(p => p + 1)}
                          >
                            Next <ChevronRight size={14} />
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </Card>
            )}

          </div>
        )}

        {/* ── Game History tab ──────────────────────────────────────────── */}
        {tab === 'history' && (
          <div className="flex flex-col gap-4">
            {games.length === 0 ? (
              <div className="text-center text-[#555566] py-8">No games played yet. Jump in!</div>
            ) : (
              games.map((g, i) => (
                <Card key={i} className="flex items-center gap-4 py-3">
                  {/* Trophy for wins, skull for losses */}
                  <div className={`flex-shrink-0 text-2xl ${g.win ? 'text-[#f0a030]' : 'text-[#555566]'}`}>
                    {g.win ? <Trophy size={24} /> : '💀'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold text-white">
                      {g.win ? 'Victory' : 'Defeat'}
                    </div>
                    <div className="text-xs text-[#888899]">
                      {new Date(g.start_time).toLocaleDateString()} · Score: {g.score}
                    </div>
                  </div>
                  <Badge variant={g.win ? 'success' : 'danger'}>
                    {g.win ? 'Win' : 'Loss'}
                  </Badge>
                </Card>
              ))
            )}

            {/* Pagination for game history */}
            {(gamePage > 0 || hasMoreGames) && (
              <div className="flex items-center justify-center gap-3">
                <Button
                  variant="secondary" size="sm"
                  disabled={gamePage === 0}
                  onClick={() => setGamePage(p => p - 1)}
                >
                  <ChevronLeft size={14} /> Prev
                </Button>
                <span className="text-sm text-[#888899]">Page {gamePage + 1}</span>
                <Button
                  variant="secondary" size="sm"
                  disabled={!hasMoreGames}
                  onClick={() => setGamePage(p => p + 1)}
                >
                  Next <ChevronRight size={14} />
                </Button>
              </div>
            )}
          </div>
        )}

      </main>
    </div>
  )
}
