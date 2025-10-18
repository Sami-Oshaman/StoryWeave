// import { StrictMode } from 'react'
// import { createRoot } from 'react-dom/client'
// import './index.css'
// import App from './App.jsx'

// createRoot(document.getElementById('root')).render(
//   <StrictMode>
//     <App />
//   </StrictMode>,
// )

import React from 'react'
import ReactDOM from 'react-dom/client'
import StoryWeaveApp from './App.jsx'       // make sure this file exists
import './index.css'             // Tailwind CSS import

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <StoryWeaveApp />
  </React.StrictMode>
)