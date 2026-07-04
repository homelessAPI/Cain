import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'

function App() {
  const [username, setUsername] = useState("")

  async function handleSubmit(e) {
    e.preventDefault()
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
    </>
  )
}

export default App
