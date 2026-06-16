// main.tsx — THE ENTRY POINT of the entire React application.
//
// React needs one HTML element to "mount" into. In index.html there is:
//   <div id="root"></div>
// This file finds that div and tells React to render our <App /> component inside it.
// Every component, page, and UI element you see on screen flows down from <App />.

import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(<App />)
