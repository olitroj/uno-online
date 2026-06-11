// App.tsx — THE ROUTER. Decides which page component to show based on the URL.
//
// How React Router works:
//   <BrowserRouter>  — wraps the whole app and watches the browser address bar
//   <Routes>         — looks at the current URL and picks the first matching <Route>
//   <Route>          — maps a URL path to a component (our "pages")
//
// Our three pages:
//   /       → AuthPage   (login / register screen)
//   /home   → HomePage   (profile, friends, game history)
//   /game   → GamePage   (the actual UNO game board)
//   *       → redirect back to / for any unknown URL (e.g. /blah → /)
//
// Navigation between pages is done with useNavigate() inside each page component,
// e.g.  navigate('/home')  after a successful login.

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AuthPage from '@/pages/AuthPage'
import HomePage from '@/pages/HomePage'
import GamePage from '@/pages/GamePage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"     element={<AuthPage />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/game" element={<GamePage />} />
        {/* Redirect any unknown path back to auth */}
        <Route path="*"     element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
