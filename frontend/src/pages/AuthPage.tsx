// pages/AuthPage.tsx — LOGIN AND REGISTER PAGE (route: "/")
//
// This is the first screen the user sees. It has two tabs: Login and Register.
// Switching tabs just changes which form is visible — the component does not unmount.
//
// FORM VALIDATION (teacher requirement):
//   We use TWO layers of validation:
//
//   Layer 1 — HTML attributes on the <input> elements:
//     required      → the browser blocks form submission if the field is empty
//     minLength={3} → browser blocks if fewer than 3 characters
//     maxLength={32} → browser stops the user from typing past 32 characters
//     pattern="[A-Za-z0-9_]+" → browser validates with this regex (letters, digits, _)
//     type="password" → browser hides the characters
//
//   Layer 2 — JavaScript inside validateRegister():
//     Checks things HTML attributes can't check, like "do the two passwords match?".
//     Returns an error string if invalid, or '' (empty string) if valid.
//     We check this BEFORE calling the API so we don't waste a network request.
//
// FLOW:
//   Login:    fill form → handleLogin() → login() API → navigate('/home')
//   Register: fill form → validateRegister() → register() API → login() API → navigate('/home')

import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { login, register } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'

// Returns an error message string if the input is invalid, or '' if everything is fine.
// Called before the register API request so we catch obvious mistakes immediately.
function validateRegister(password: string, confirm: string): string {
  if (password.length < 6)   return 'Password must be at least 8 characters.'
  if (password !== confirm)  return 'Passwords do not match.'
  return ''
}

export default function AuthPage() {
  const navigate = useNavigate()

  // tab controls which form is shown: 'login' or 'register'
  const [tab, setTab]         = useState<'login' | 'register'>('login')
  // error holds a message shown in the red banner above the form
  const [error, setError]     = useState('')
  // loading is true while an API call is in flight — disables the submit button
  const [loading, setLoading] = useState(false)

  // Called when the login form is submitted.
  // e.preventDefault() stops the browser from reloading the page (default form behaviour).
  async function handleLogin(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    // Read field values directly from the form DOM element by their name attribute
    const form     = e.currentTarget
    const username = (form.elements.namedItem('username') as HTMLInputElement).value
    const password = (form.elements.namedItem('password') as HTMLInputElement).value

    setError('')
    setLoading(true)
    try {
      await login(username, password)    // POST /me/token — sets the auth cookie
      navigate('/home')                  // redirect to home page on success
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)  // always re-enable the button, even if the API call failed
    }
  }

  // Called when the register form is submitted.
  async function handleRegister(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const form     = e.currentTarget
    const username = (form.elements.namedItem('username') as HTMLInputElement).value
    const password = (form.elements.namedItem('password') as HTMLInputElement).value
    const confirm  = (form.elements.namedItem('confirm')  as HTMLInputElement).value

    // JS validation layer — check before making any API call
    const validationError = validateRegister(password, confirm)
    if (validationError) { setError(validationError); return }

    setError('')
    setLoading(true)
    try {
      await register(username, password)     // POST /me — creates the account
      await login(username, password)        // POST /me/token — log in immediately
      navigate('/home')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f0f13] px-4">
      <div className="w-full max-w-sm">

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-2">🐱</div>
          <h1 className="text-3xl font-black text-white">Cat UNO</h1>
          <p className="text-[#888899] text-sm mt-1">Multiplayer card game</p>
        </div>

        {/* Tab switcher — clicking a tab changes the 'tab' state */}
        <div className="flex rounded-lg bg-[#1a1a2e] p-1 mb-6">
          <button
            onClick={() => { setTab('login'); setError('') }}
            className={`flex-1 py-2 rounded-md text-sm font-semibold transition-all ${
              tab === 'login'
                ? 'bg-[#6c63ff] text-white'
                : 'text-[#888899] hover:text-white'
            }`}
          >
            Login
          </button>
          <button
            onClick={() => { setTab('register'); setError('') }}
            className={`flex-1 py-2 rounded-md text-sm font-semibold transition-all ${
              tab === 'register'
                ? 'bg-[#6c63ff] text-white'
                : 'text-[#888899] hover:text-white'
            }`}
          >
            Register
          </button>
        </div>

        {/* Error banner — only rendered when error is a non-empty string */}
        {error && (
          <div className="mb-4 rounded-lg bg-[#3a1a1a] border border-[#e05555]/40 px-4 py-3 text-sm text-[#e05555]">
            {error}
          </div>
        )}

        {/* ── Login form — shown when tab === 'login' ── */}
        {tab === 'login' && (
          <form onSubmit={handleLogin} className="flex flex-col gap-4">
            <Input
              id="username"
              name="username"           // name is used by form.elements.namedItem()
              label="Username"
              placeholder="Enter your username"
              required                  // HTML: blocks submit if empty
              autoFocus
            />
            <Input
              id="password"
              name="password"
              type="password"           // hides the characters
              label="Password"
              placeholder="Enter your password"
              required
            />
            <Button type="submit" size="lg" disabled={loading} className="mt-2 w-full">
              {loading ? 'Logging in…' : 'Login'}
            </Button>
          </form>
        )}

        {/* ── Register form — shown when tab === 'register' ── */}
        {tab === 'register' && (
          <form onSubmit={handleRegister} className="flex flex-col gap-4">
            <Input
              id="username"
              name="username"
              label="Username"
              placeholder="Choose a username"
              required
              pattern="[A-Za-z0-9_]+"   // HTML: only allow letters, digits, underscore
              autoFocus
            />
            <Input
              id="password"
              name="password"
              type="password"
              label="Password"
              placeholder="Choose a password"
              required
              minLength={6}
              maxLength={64}
            />
            <Input
              id="confirm"
              name="confirm"
              type="password"
              label="Confirm Password"
              placeholder="Repeat your password"
              required
              minLength={6}
              maxLength={64}
            />
            <Button type="submit" size="lg" disabled={loading} className="mt-2 w-full">
              {loading ? 'Creating account…' : 'Create Account'}
            </Button>
          </form>
        )}

      </div>
    </div>
  )
}
