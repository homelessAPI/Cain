import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'

function App() {
  const [username, setUsername] = useState("")
  const [events, setEvents] = useState([])
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    try {
      const user = {
      username: username
    }

    const response = await fetch("http://127.0.0.1:5000/",
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(user)
      }
    )
    const data = await response.json()
    console.log(data)

    if (!response.ok) {
      setEvents([])
      setError(data.detail || "An error occurred while fetching events.")
    } else {
      setError(null)
      setEvents(data.events)
    }
    }
    catch (error) {
      setEvents([])
      setError("An error occurred while fetching events.")
    }
  }

  return (
    <>
      <div className="user-input">
        <fieldset>
          <legend>Input</legend>
          <input type="text" placeholder='Username' value={username} onChange={(e) => setUsername(e.target.value)}/>
          <button onClick={handleSubmit}>Submit</button>
        </fieldset>
      </div>
      <div className="output">
        {error && <p className='error'>{error}</p>}
        <ul>
          {events.map((event, index) => (
            <li key={index}>
              {event.type} - {event.repository}
            </li>
          ))}
        </ul>
      </div>
    </>
  )
}

export default App
