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

function QualityBar({ name, score }) {
  const safeScore = Number.isFinite(score) ? Math.max(0, Math.min(100, score)) : 0;

  return (
    <div className="quality-category">
      <div className="quality-category-header">
        <span>{name}</span>
        <strong>{Number.isFinite(score) ? `${safeScore.toFixed(1)}%` : "—"}</strong>
      </div>

      <div className="quality-bar-background">
        <div
          className="quality-bar-fill"
          style={{ width: `${safeScore}%` }}
        />
      </div>
    </div>
  );
}

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

  const chartData = Object.entries(weekday || {}).map(
    ([day, events]) => ({ day, events })
  );

  function clearData() {
    setEvents([]);
    setUser(null);
    setRepos([]);
    setLanguages([]);
    setWeekday({});
    setQuality(null);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const requestData = { username: username.trim() };

      if (!requestData.username) {
        clearData();
        setError("Please enter a GitHub username.");
        return;
      }

      localStorage.setItem("Github_Username", requestData.username);

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
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

      localStorage.setItem("data", JSON.stringify(data));

      setEvents(data.events || []);
      setUser(data.users || null);
      setRepos(data.repos || []);
      setWeekday(data.Weekly_usage || {});
      setLanguages(data.languages || []);
      setQuality(data.quality || null);
    } catch (error) {
      console.error(error);
      clearData();
      setError("Unable to connect to the Cain backend.");
    } finally {
      setLoading(false);
    }
  }

  const categories = quality?.Categories
    ? [
        { name: "Documentation", score: quality.Categories.documentation },
        { name: "Engineering", score: quality.Categories.engineering },
        { name: "Repository Hygiene", score: quality.Categories.repo_hygiene },
        { name: "DevOps", score: quality.Categories.devops }
      ]
    : [];

  return (
    <>
      <Navbar />

      <main>
        <div className="user-input">
          <fieldset className="input-fieldset">
            <legend>Analyze a GitHub profile</legend>

            <form onSubmit={handleSubmit}>
              <input
                type="text"
                className="username"
                placeholder="GitHub username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                aria-label="GitHub username"
              />

              <button type="submit" disabled={loading}>
                {loading ? "Analyzing..." : "Analyze"}
              </button>
            </form>
          </fieldset>
        </div>

        {error && (
          <div className="error-container">
            <p className="error">{error}</p>
          </div>
        )}

        <div className="output">
          {user && (
            <fieldset className="user-output-fieldset">
              <legend>Profile</legend>

              <div className="profile-card">
                <img
                  src={user.profile}
                  alt={`${username}'s GitHub profile`}
                />

                <h1>{username}</h1>

                <div className="profile-stats">
                  <div>
                    <strong>{user.followers}</strong>
                    <span>Followers</span>
                  </div>
                  <div>
                    <strong>{user.following}</strong>
                    <span>Following</span>
                  </div>
                  <div>
                    <strong>{user.public_repos}</strong>
                    <span>Public repos</span>
                  </div>
                </div>

                <p className="company">
                  {user.company ? `Company: ${user.company}` : "No company listed"}
                </p>
              </div>
            </fieldset>
          )}

          {quality && (
            <fieldset className="quality-output-fieldset">
              <legend>Repository Quality</legend>

              <div className="quality-score">
                <span className="quality-label">Overall score</span>

                <div className="quality-score-number">
                  {Number.isFinite(quality.Score)
                    ? quality.Score.toFixed(1)
                    : "—"}
                  <span>/100</span>
                </div>

                <div className="quality-grade">
                  Grade: {quality.Grade || "N/A"}
                </div>

                <div className="quality-categories">
                  {categories.map((category) => (
                    <QualityBar
                      key={category.name}
                      name={category.name}
                      score={category.score}
                    />
                  ))}
                </div>
              </div>
            </fieldset>
          )}

          {(chartData.length > 0 || languages.length > 0) && (
            <fieldset className="analysis-output-fieldset">
              <legend>Activity Analysis</legend>

              <div className="analysis-grid">
                {chartData.length > 0 && (
                  <section className="analysis-card">
                    <h2>Weekly Activity</h2>
                    <ResponsiveContainer width="100%" height={320}>
                      <BarChart
                        data={chartData}
                        margin={{ top: 20, right: 20, left: 0, bottom: 10 }}
                      >
                        <defs>
                          <linearGradient
                            id="barGradient"
                            x1="0"
                            y1="0"
                            x2="0"
                            y2="1"
                          >
                            <stop offset="0%" stopColor="#6366f1" />
                            <stop offset="100%" stopColor="#a855f7" />
                          </linearGradient>
                        </defs>

                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="day" tick={{ fill: "#8b949e", fontSize: 12 }} />
                        <YAxis allowDecimals={false} tick={{ fill: "#8b949e" }} />
                        <Tooltip
                          cursor={{ fill: "rgba(99,102,241,0.1)" }}
                          contentStyle={{
                            backgroundColor: "#ffffff",
                            borderRadius: "10px",
                            border: "1px solid #d1d5db",
                            boxShadow: "0 8px 20px rgba(0,0,0,.18)"
                          }}
                          labelStyle={{ color: "#111827", fontWeight: "600" }}
                          itemStyle={{ color: "#374151" }}
                        />
                        <Bar
                          dataKey="events"
                          fill="url(#barGradient)"
                          radius={[10, 10, 0, 0]}
                          animationDuration={800}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </section>
                )}

                {languages.length > 0 && (
                  <section className="analysis-card">
                    <h2>Languages</h2>
                    <ResponsiveContainer width="100%" height={320}>
                      <BarChart
                        data={languages}
                        layout="vertical"
                        margin={{ top: 15, right: 20, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                        <XAxis type="number" allowDecimals={false} />
                        <YAxis type="category" dataKey="language" width={90} />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "#ffffff",
                            borderRadius: "10px",
                            border: "1px solid #d1d5db",
                            boxShadow: "0 8px 20px rgba(0,0,0,.18)"
                          }}
                          labelStyle={{ color: "#111827", fontWeight: "600" }}
                          itemStyle={{ color: "#374151" }}
                        />
                        <Bar dataKey="count" radius={[0, 8, 8, 0]}>
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
                  </section>
                )}
              </div>
            </fieldset>
          )}

          <fieldset className="events-output-fieldset">
            <legend>Recent Activity</legend>

            {events.length === 0 ? (
              <p className="empty-state">No recent public events found.</p>
            ) : (
              <div className="events-table-wrapper">
                <table className="events-list">
                  <thead>
                    <tr className="events-list-header">
                      <th>Event Type</th>
                      <th>Repository</th>
                      <th>Created At</th>
                      <th>Public</th>
                    </tr>
                  </thead>
                  <tbody>
                    {events.map((event, index) => (
                      <tr key={index}>
                        <td>{event.type}</td>
                        <td>
                          <a
                            className="link"
                            href={event.repository_url}
                            target="_blank"
                            rel="noreferrer"
                          >
                            {event.repository?.split("/")[1] || "Unknown"}
                          </a>
                        </td>
                        <td>{new Date(event.created_at).toLocaleString()}</td>
                        <td>{event.public ? "Yes" : "No"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </fieldset>
        </div>
      </main>
    </>
  );
}

export default Home;
