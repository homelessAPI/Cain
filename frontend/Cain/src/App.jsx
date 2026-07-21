import { useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  Cell
} from "recharts";
import './App.css'

function App() {
  const [username, setUsername] = useState("")
  const [events, setEvents] = useState([])
  const [repos, setRepos] = useState([])
  const [weekday, setWeekday] = useState({})
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [user, setUser] = useState(null)
  const [languages, setLanguages] = useState([])

  const chartData = Object.entries(weekday).map(
      ([day, events]) => ({
        day,
        events
      })
    )

  async function handleSubmit(e) {
    e.preventDefault()

    setLoading(true)
    console.log(import.meta.env.VITE_API_URL)
    try {
      const user = {
      username: username
    }

    const response = await fetch(`${import.meta.env.VITE_API_URL}/`,
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
      setUser([])
      setRepos([])
      setWeekday([])
      setError(data.detail || "An error occurred while fetching events.")
    } else {
      setError(null)
      setEvents(data.events)
      setUser(data.users)
      setRepos(data.repos)
      setWeekday(data.Weekly_usage)
      setLanguages(data.languages)
    }
    }
    catch (error) {
      setEvents([])
      setUser([])
      setRepos([])
      setError("An error occurred while fetching events.")
    }
    finally {
      setLoading(false)
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
          <input type="text" className='username' placeholder='Github Username' value={username} onChange={(e) => setUsername(e.target.value)}/>
          <br />
          <button onClick={handleSubmit}>{loading? 'Searching': 'Search'}</button>
        </fieldset>
      </div>
      <div className="output">
        <div className='output'>
          <fieldset className='user-output-fieldset'>
          <legend>User Info</legend>
          {user && (
              <div>
                  <img src={user.profile} alt="Profile" />
                  <h1>Following: {user.following}</h1>
                  <h1>Followers: {user.followers}</h1>
                  <h1>Public Repos: {user.public_repos}</h1>
                  <h1>{user.company? `Company: ${user.company}` : "Company: none"}</h1>
              </div>
          )}
        </fieldset>
        <fieldset className='events-output-fieldset'>
          <legend>Output</legend>
          {error && <p className='error'>{error}</p>}
          <table className='events-list'>
            <thead>
              <tr className='events-list-header'>
                <th>Event Type</th>
                <th>Repository</th>
                <th>Created At</th>
                <th>Public</th>
              </tr>
            </thead>
            <tbody>
              {events.map((event,index) => (
                <tr key={index}>
                  <td>{event.type}</td>
                  <td>
                    <a className='link' href={event.repository_url}>{event.repository.split("/")[1]}</a>
                  </td>
                  <td>{new Date(event.created_at).toLocaleString()}</td>
                  <td>{event.public ? 'Yes' : 'No'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </fieldset>
        <fieldset className='analysis-output-fieldset'>
          <ResponsiveContainer width="100%" height={350}>

            <BarChart
              data={chartData}
              margin={{
                top: 20,
                right: 30,
                left: 10,
                bottom: 10
              }}
            >

              <defs>
                <linearGradient 
                  id="barGradient"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop 
                    offset="0%"
                    stopColor="#6366f1"
                  />

                  <stop
                    offset="100%"
                    stopColor="#a855f7"
                  />
                </linearGradient>
              </defs>


              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
              />


              <XAxis 
                dataKey="day"
                tick={{
                  fill:"#555",
                  fontSize:12
                }}
              />


              <YAxis
                allowDecimals={false}
                tick={{
                  fill:"#555"
                }}
              />


              <Tooltip
                cursor={{
                  fill:"rgba(99,102,241,0.1)"
                }}

                contentStyle={{
                  borderRadius:"10px",
                  border:"none",
                  boxShadow:"0 8px 20px rgba(0,0,0,.15)"
                }}
              />


              <Bar
                dataKey="events"

                fill="url(#barGradient)"

                radius={[
                  10,
                  10,
                  0,
                  0
                ]}

                animationDuration={800}

              />

            </BarChart>

          </ResponsiveContainer>

          <ResponsiveContainer width="100%" height={300}>
    <BarChart
        data={languages}
        layout="vertical"
        margin={{
            top: 15,
            right: 20,
            left: 20,
            bottom: 5
        }}
    >
        <CartesianGrid
            strokeDasharray="3 3"
            horizontal={false}
        />

        <XAxis
            type="number"
            allowDecimals={false}
        />

        <YAxis
            type="category"
            dataKey="language"
            width={90}
        />

        <Tooltip />

        <Bar
            dataKey="count"
            radius={[0, 8, 8, 0]}
        >
            {languages.map((entry, index) => (
                <Cell
                    key={index}
                    fill={[
                        "#6366f1",
                        "#8b5cf6",
                        "#ec4899",
                        "#f59e0b",
                        "#10b981",
                        "#06b6d4",
                        "#ef4444"
                    ][index % 7]}
                />
            ))}
        </Bar>
    </BarChart>
</ResponsiveContainer>
        </fieldset>
        </div>
      </div>
    </>
  )
}

export default App