import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { GithubProvider } from "../components/GithubContext.jsx";

createRoot(document.getElementById('root')).render(
    <GithubProvider >
      <App />
    </GithubProvider >
)
