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

    const response = await fetch("https://cain-h3k7.onrender.com/",
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
    <nav className='navbar'>
      <h1 className='Site-Name'>Cain</h1>
    </nav>
      <div className="user-input">
        <fieldset className='input-fieldset'>
          <legend>Input</legend>
          <input type="text" className='username' placeholder='Username' value={username} onChange={(e) => setUsername(e.target.value)}/>
          <br />
          <button onClick={handleSubmit}>Submit</button>
        </fieldset>
      </div>
      <div className="output">
        <fieldset className='output-fieldset'>
          <legend>Output</legend>
          {error && <p className='error'>{error}</p>}
          <table className='events-list'>
            <thead>
              <tr className='events-list-header'>
                <th>Event Type</th>
                <th>Repository</th>
                <th>Repository URL</th>
                <th>Created At</th>
                <th>Public</th>
              </tr>
            </thead>
            <tbody>
              {events.map((event,index) => (
                <tr key={index}>
                  <td>{event.type}</td>
                  <td>{event.repository}</td>
                  <td>{event.repository_url}</td>
                  <td>{event.created_at}</td>
                  <td>{event.public ? 'Yes' : 'No'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </fieldset>
      </div>
    </>
  )
}

export default App
