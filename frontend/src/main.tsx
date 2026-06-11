// main.tsx — THE ENTRY POINT of the entire React application.
//
// React needs one HTML element to "mount" into. In index.html there is:
//   <div id="root"></div>
// This file finds that div and tells React to render our <App /> component inside it.
// Every component, page, and UI element you see on screen flows down from <App />.
//
// WHY is StrictMode removed?
//   React's StrictMode is a development tool that intentionally runs every
//   useEffect TWICE (mount → unmount → mount again) to help find bugs.
//   Our WebSocket hook opens a connection inside useEffect. With StrictMode,
//   two connections are opened simultaneously and the game server rejects the
//   second one with "already connected". Removing StrictMode prevents this.

import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(<App />)
