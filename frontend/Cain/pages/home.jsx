import { useContext, useState } from "react";
import { GithubContext } from "../components/GithubContext.jsx";

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

import "./home.css";
import Navbar from "../components/Navbar";


function Home() {

  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);


  const {
    username,
    setUsername,

    user,
    setUser,

    events,
    setEvents,

    repos,
    setRepos,

    languages,
    setLanguages,

    weekday,
    setWeekday,

    quality,
    setQuality

  } = useContext(GithubContext);


  // --------------------------------
  // Chart data
  // --------------------------------

  const chartData = Object.entries(weekday).map(
    ([day, events]) => ({
      day,
      events
    })
  );


  // --------------------------------
  // Clear previous GitHub data
  // --------------------------------

  function clearData() {

    setEvents([]);
    setUser(null);
    setRepos([]);
    setLanguages([]);
    setWeekday({});
    setQuality(null);
  }


  // --------------------------------
  // Search GitHub user
  // --------------------------------

  async function handleSubmit(e) {

    e.preventDefault();

    setLoading(true);
    setError(null);


    try {

      const requestData = {
        username: username.trim()
      };


      if (!requestData.username) {

        clearData();

        setError("Please enter a GitHub username.");

        return;
      }


      localStorage.setItem(
        "Github_Username",
        requestData.username
      );


      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify(requestData)
        }
      );


      const data = await response.json();


      if (!response.ok) {

        clearData();

        setError(
          data.detail ||
          "An error occurred while fetching GitHub data."
        );

        return;
      }


      // Store response locally for development/debugging.
      localStorage.setItem(
        "data",
        JSON.stringify(data)
      );


      // --------------------------------
      // Update global application state
      // --------------------------------

      setEvents(data.events || []);

      setUser(data.users || null);

      setRepos(data.repos || []);

      setWeekday(data.Weekly_usage || {});

      setLanguages(data.languages || []);

      setQuality(data.quality || null);

    }


    catch (error) {

      console.error(error);

      clearData();

      setError(
        "Unable to connect to the Cain backend."
      );
    }


    finally {

      setLoading(false);
    }
  }


  return (
    <>
      <Navbar />


      {/* -------------------------------- */}
      {/* Search */}
      {/* -------------------------------- */}

      <div className="user-input">

        <fieldset className="input-fieldset">

          <legend>Input</legend>

          <input
            type="text"
            className="username"
            placeholder="Github Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <br />

          <button
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? "Searching..." : "Search"}
          </button>

        </fieldset>

      </div>


      {/* -------------------------------- */}
      {/* Output */}
      {/* -------------------------------- */}

      <div className="output">

        {/* -------------------------------- */}
        {/* User information */}
        {/* -------------------------------- */}

        <fieldset className="user-output-fieldset">

          <legend>User Info</legend>

          {user && (

            <div>

              <img
                src={user.profile}
                alt={`${username}'s GitHub profile`}
              />

              <h1>
                Following: {user.following}
              </h1>

              <h1>
                Followers: {user.followers}
              </h1>

              <h1>
                Public Repos: {user.public_repos}
              </h1>

              <h1>
                {user.company
                  ? `Company: ${user.company}`
                  : "Company: none"
                }
              </h1>

            </div>

          )}

        </fieldset>


        {/* -------------------------------- */}
        {/* Repository quality */}
        {/* -------------------------------- */}

        {quality && (

          <fieldset className="quality-output-fieldset">

            <legend>Repository Quality</legend>

            <div className="quality-score">

              <h2>
                Repository Quality
              </h2>

              <h1>
                {quality.Score.toFixed(1)}/100
              </h1>

              <h2>
                Grade: {quality.Grade}
              </h2>

              <div className="quality-categories">

              <div>
                  <h3>Documentation</h3>
                  <p>
                      {quality.Categories.documentation.toFixed(1)}%
                  </p>
              </div>

              <div>
                  <h3>Engineering</h3>
                  <p>
                      {quality.Categories.engineering.toFixed(1)}%
                  </p>
              </div>

              <div>
                  <h3>Repository Hygiene</h3>
                  <p>
                      {quality.Categories.repo_hygiene.toFixed(1)}%
                  </p>
              </div>

              <div>
                  <h3>DevOps</h3>
                  <p>
                      {quality.Categories.devops.toFixed(1)}%
                  </p>
              </div>

          </div>

            </div>

          </fieldset>

        )}


        {/* -------------------------------- */}
        {/* Analysis */}
        {/* -------------------------------- */}

        <fieldset className="analysis-output-fieldset">


          {/* Weekly activity */}

          <ResponsiveContainer
            width="100%"
            height={350}
          >

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
                  fill: "#555",
                  fontSize: 12
                }}
              />


              <YAxis
                allowDecimals={false}
                tick={{
                  fill: "#555"
                }}
              />


             <Tooltip
  cursor={{
    fill: "rgba(99,102,241,0.1)"
  }}
  contentStyle={{
    backgroundColor: "#ffffff",
    borderRadius: "10px",
    border: "1px solid #e5e7eb",
    boxShadow: "0 8px 20px rgba(0,0,0,.15)",
    color: "#111827"
  }}
  labelStyle={{
    color: "#111827",
    fontWeight: "600"
  }}
  itemStyle={{
    color: "#374151"
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


          {/* Language analysis */}

          <ResponsiveContainer
            width="100%"
            height={300}
          >

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


              <Tooltip
  contentStyle={{
    backgroundColor: "#ffffff",
    borderRadius: "10px",
    border: "1px solid #e5e7eb",
    boxShadow: "0 8px 20px rgba(0,0,0,.15)"
  }}
  labelStyle={{
    color: "#111827",
    fontWeight: "600"
  }}
  itemStyle={{
    color: "#374151"
  }}
/>

              <Bar
                dataKey="count"
                radius={[
                  0,
                  8,
                  8,
                  0
                ]}
              >

                {languages.map(
                  (entry, index) => (

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

                  )
                )}

              </Bar>

            </BarChart>

          </ResponsiveContainer>


        </fieldset>

      </div>

      {/* -------------------------------- */}
        {/* GitHub events */}
        {/* -------------------------------- */}

        <fieldset className="events-output-fieldset">

          <legend>Activity</legend>


          {error && (
            <p className="error">
              {error}
            </p>
          )}


          <table className="events-list">

            <thead>

              <tr className="events-list-header">

                <th>
                  Event Type
                </th>

                <th>
                  Repository
                </th>

                <th>
                  Created At
                </th>

                <th>
                  Public
                </th>

              </tr>

            </thead>


            <tbody>

              {events.map((event, index) => (

                <tr key={index}>

                  <td>
                    {event.type}
                  </td>


                  <td>

                    <a
                      className="link"
                      href={event.repository_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {event.repository.split("/")[1]}
                    </a>

                  </td>


                  <td>
                    {new Date(
                      event.created_at
                    ).toLocaleString()}
                  </td>


                  <td>
                    {event.public ? "Yes" : "No"}
                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </fieldset>
    </>
  );
}


export default Home;