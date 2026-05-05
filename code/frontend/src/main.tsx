import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Log application startup - visible in browser console
console.clear();
console.log('%c\n🚀 Healthcare RAG System - Frontend Started\n', 'color: #3b82f6; font-size: 18px; font-weight: bold; background: #f0f9ff; padding: 10px; border-radius: 5px;');
console.log('%cURL: http://localhost:5173', 'color: #10b981; font-size: 13px; font-weight: bold;');
console.log('%cAPI: http://localhost:8000', 'color: #10b981; font-size: 13px; font-weight: bold;');
console.log('%cOpen browser DevTools (F12) to see logs', 'color: #f59e0b; font-size: 12px; font-style: italic;');
console.log('');

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
