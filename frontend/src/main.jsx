/**
 * main.jsx
 *
 * The entry point for the React application.
 * This file imports the global CSS, the root App component, and renders the application
 * into the DOM element with the id "root" using React 18's createRoot API in StrictMode.
 *
 * @module main
 */

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
