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

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        clearData();

        const detail = data.detail;
        const message =
          typeof detail === "string"
            ? detail
            : detail?.message;

        if (response.status === 404) {
          setError(
            message ||
            `No GitHub account was found for "${requestData.username}". Use the @username/login shown in the profile URL, not the display name at the top of the profile.`
          );
        } else if (response.status === 429) {
          setError(
            message ||
            "GitHub is temporarily limiting requests. Please wait a little while before trying again."
          );
        } else if (response.status === 502 || response.status === 503) {
          setError(
            message ||
            "Cain could not retrieve data from GitHub. GitHub may be temporarily unavailable; please try again."
          );
        } else if (response.status >= 500) {
          setError(
            message ||
            "Cain ran into an internal problem while analyzing this profile. Please try again later."
          );
        } else {
          setError(message || "Cain could not complete the GitHub profile lookup.");
        }
        return;
      }

      localStorage.setItem("data", JSON.stringify(data));

      setUser(data.users || null);
      setRepos(data.repos || []);
      setWeekday(data.Weekly_usage || {});
      setLanguages(data.languages || []);

      setQuality({
        documentation_quality: data.documentation_quality || {},
        documentation_scores: data.documentation_scores || {},
        documentation_reasons: data.documentation_reasons || {},
        total_documentation_score: data.total_documentation_score || 0,
        max_documentation_score: data.max_documentation_score || 0,
        documentation_percentage: data.documentation_percentage || 0,
        maintenance: data.maintenance || {},
        maintenance_total_score: data.maintenance_total_score || 0,
        maintenance_max_score: data.maintenance_max_score || 0,
        maintenance_percentage: data.maintenance_percentage || 0,
        project_hygiene: data.project_hygiene || {},
        project_hygiene_total_score: data.project_hygiene_total_score || 0,
        project_hygiene_max_score: data.project_hygiene_max_score || 0,
        project_hygiene_percentage: data.project_hygiene_percentage || 0,
        project_hygiene_scanned_count: data.project_hygiene_scanned_count || 0,
        project_hygiene_total_count: data.project_hygiene_total_count || 0,
        profile_level: data.profile_level || {},
        overall_percentage: data.overall_percentage || 0,
        overall_grade: data.overall_grade || "C"
      });
    } catch (error) {
      console.error(error);
      clearData();
      setError(
        "Unable to connect to Cain. The backend may be offline or unreachable; please try again later."
      );
    } finally {
      setLoading(false);
    }
  }

  const documentationResults = quality
    ? Object.entries(quality.documentation_scores || {})
    : [];

  const maintenanceResults = quality
    ? Object.entries(quality.maintenance || {})
    : [];

  const hygieneResults = quality
    ? Object.entries(quality.project_hygiene || {})
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
          <div className="profile-column">
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
          </div>
          {quality && (
            <div className="assessment-column">
                          <fieldset className="overall-score-fieldset">
              <legend>Overall Repository Assessment</legend>
              <div className="overall-score-content">
                <div>
                  <span className="quality-label">Average across four assessment areas</span>
                  <div className="overall-grade">{quality.overall_grade}</div>
                  <div className="overall-percentage">{quality.overall_percentage}%</div>
                </div>
                <div className="overall-score-breakdown">
                  <span>Documentation: {quality.documentation_percentage}%</span>
                  <span>Maintenance: {quality.maintenance_percentage}%</span>
                  <span>Project hygiene: {quality.project_hygiene_percentage}%</span>
                  <span>Profile Level: qualitative signals included in the average</span>
                </div>
              </div>
              <p className="score-explanation">
                A: 85–100 · B: 70–84.9 · C: below 70. The overall grade is the
                simple average of Documentation, Maintenance, Project Hygiene,
                and the internal Profile Level assessment. Profile Level displays
                improvement signals instead of a points total.
              </p>
            </fieldset>
              <div className="assessment-grid">
                                <fieldset className="quality-output-fieldset">
                <legend>Documentation</legend>

                <div className="score-summary">
                  <span className="quality-label">Total documentation score</span>
                  <div className="quality-score-number">
                    {quality.total_documentation_score}
                    <span>/{quality.max_documentation_score}</span>
                  </div>
                  <div className="quality-grade">
                    {quality.documentation_percentage}% across all repositories
                  </div>
                  <p className="score-explanation">
                    Each repository can earn 5 points: one for each README section
                    (Features, Installation, Usage, Tech Stack, and License) that
                    exists and contains content.
                  </p>
                </div>

                <div className="score-repositories" aria-label="Individual documentation scores">
                  {documentationResults.map(([repoName, score]) => {
                    const reasons = quality.documentation_reasons?.[repoName] || {};
                    const grade = quality.documentation_quality?.[repoName] || "N/A";

                    return (
                      <div className="score-repository" key={repoName}>
                        <div className="score-repository-header">
                          <div>
                            <h3>{repoName}</h3>
                            <span className="score-grade">{grade}</span>
                          </div>
                          <strong>{score}/5</strong>
                        </div>
                        <div className="quality-bar-background">
                          <div
                            className="quality-bar-fill"
                            style={{ width: `${score * 20}%` }}
                          />
                        </div>
                        <div className="score-reasons">
                          {(reasons.earned || []).map((reason, index) => (
                            <p className="reason-earned" key={index}>
                              <span>+</span> {reason}
                            </p>
                          ))}
                          {(reasons.missing || []).map((reason, index) => (
                            <p className="reason-missing" key={index}>
                              <span>−</span> {reason}
                            </p>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </fieldset>
                                <fieldset className="maintenance-output-fieldset">
                <legend>Maintenance</legend>

                <div className="score-summary">
                  <span className="quality-label">Total maintenance score</span>
                  <div className="quality-score-number">
                    {quality.maintenance_total_score}
                    <span>/{quality.maintenance_max_score}</span>
                  </div>
                  <div className="quality-grade">
                    {quality.maintenance_percentage}% across eligible repositories
                  </div>
                  <p className="score-explanation">
                    Each active repository can earn up to 10 points: 5 for how
                    recently it was pushed to and 5 for commit activity across
                    the last six months. Archived repositories are excluded.
                    If commit history cannot be retrieved, only the 5 recency
                    points are scored.
                  </p>
                </div>

                <div className="score-repositories" aria-label="Individual maintenance scores">
                  {maintenanceResults.map(([repoName, result]) => {
                    const score = result.score;
                    const maxScore = result.max_score;
                    const scorePercent = maxScore ? (score / maxScore) * 100 : 0;

                    return (
                      <div className="score-repository" key={repoName}>
                        <div className="score-repository-header">
                          <div>
                            <h3>{repoName}</h3>
                            <span className="score-grade">{result.grade}</span>
                          </div>
                          <strong>
                            {score === null ? "—" : `${score}/${maxScore}`}
                          </strong>
                        </div>

                        {maxScore > 0 && (
                          <div className="quality-bar-background">
                            <div
                              className="quality-bar-fill maintenance-bar-fill"
                              style={{ width: `${scorePercent}%` }}
                            />
                          </div>
                        )}

                        <div className="maintenance-details">
                          <span>
                            Last push: {result.days_since_last_push === null
                              ? "Unknown"
                              : result.days_since_last_push === 0
                                ? "Today"
                                : `${result.days_since_last_push} days ago`}
                          </span>
                          <span>
                            Commit activity: {result.active_months === null
                              ? "Unavailable"
                              : `${result.active_months}/6 active months`}
                          </span>
                          <span>
                            Commits observed: {result.commits_last_six_months === null
                              ? "Unavailable"
                              : result.commits_last_six_months}
                            {result.history_capped ? " (retrieval limit reached)" : ""}
                          </span>
                        </div>

                        <div className="score-reasons">
                          {(result.reasons || []).map((reason, index) => (
                            <p className="maintenance-reason" key={index}>{reason}</p>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </fieldset>
                              <fieldset className="hygiene-output-fieldset">
                <legend>Project Hygiene</legend>
                <div className="score-summary">
                  <span className="quality-label">Project hygiene score</span>
                  <div className="quality-score-number">
                    {quality.project_hygiene_total_score}
                    <span>/{quality.project_hygiene_max_score}</span>
                  </div>
                  <div className="quality-grade">
                    {quality.project_hygiene_percentage}% · {quality.project_hygiene_scanned_count} of {quality.project_hygiene_total_count} repositories inspected
                  </div>
                  <p className="score-explanation">
                    Cain checks tracked files for generated folders, local environment
                    files, possible secrets, large binaries, temporary filenames,
                    dependency manifests, lockfiles, licenses, and code-quality
                    configuration. File-tree scanning is limited to the 30 most
                    recently pushed repositories.
                  </p>
                </div>
                <div className="score-repositories" aria-label="Individual project hygiene results">
                  {hygieneResults.map(([repoName, result]) => (
                    <div className="score-repository" key={repoName}>
                      <div className="score-repository-header">
                        <div>
                          <h3>{repoName}</h3>
                          <span className="score-grade">{result.available ? result.grade : "Not inspected"}</span>
                        </div>
                        <strong>{result.score === null ? "—" : `${result.score}/10`}</strong>
                      </div>
                      {result.available && (
                        <div className="quality-bar-background">
                          <div className="quality-bar-fill hygiene-bar-fill" style={{ width: `${result.score * 10}%` }} />
                        </div>
                      )}
                      {result.truncated && (
                        <p className="hygiene-warning">GitHub returned a truncated file tree; some files may not have been inspected.</p>
                      )}
                      <div className="score-reasons">
                        {(result.findings || []).map((finding, index) => (
                          <p className="reason-missing" key={index}>
                            <span>!</span> [{finding.severity}] {finding.path}: {finding.message}
                          </p>
                        ))}
                        {(result.good_signs || []).map((reason, index) => (
                          <p className="reason-earned" key={index}><span>+</span> {reason}</p>
                        ))}
                        {(result.missing_signs || []).map((reason, index) => (
                          <p className="hygiene-neutral" key={index}><span>·</span> {reason}</p>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </fieldset>
                              <fieldset className="profile-level-output-fieldset">
                <legend>Profile Level</legend>
                <div className="score-summary">
                  <span className="quality-label">Profile assessment</span>
                  <div className="profile-level-name">{quality.profile_level?.level || "Insufficient data"}</div>
                  <div className="quality-grade">Account age: {quality.profile_level?.account_age || "Unavailable"}</div>
                  <p className="score-explanation">
                    Account age is context, not a penalty. Strong project work on a
                    newer account can earn additional recognition. This assessment
                    looks at public pull requests, recent public contributions,
                    pinned repositories, language range, and standout project quality.
                  </p>
                </div>
                <div className="profile-signal-grid">
                  <div><strong>{quality.profile_level?.public_pull_requests ?? "—"}</strong><span>Public PRs</span></div>
                  <div><strong>{quality.profile_level?.merged_pull_requests ?? "—"}</strong><span>Merged PRs</span></div>
                  <div><strong>{quality.profile_level?.recent_public_events ?? "—"}</strong><span>Recent public events</span></div>
                  <div><strong>{quality.profile_level?.recent_push_events ?? "—"}</strong><span>Recent push events</span></div>
                </div>
                <div className="profile-signal-section">
                  <h3>Pinned repositories</h3>
                  {quality.profile_level?.pinned_repositories == null ? (
                    <p className="hygiene-neutral">Could not verify pinned repositories automatically.</p>
                  ) : quality.profile_level.pinned_repositories.length ? (
                    <ul>
                      {quality.profile_level.pinned_repositories.map((repoName) => (
                        <li key={repoName}><a href={`https://github.com/${repoName}`} target="_blank" rel="noreferrer">{repoName}</a></li>
                      ))}
                    </ul>
                  ) : (
                    <p className="reason-missing">No pinned repositories detected. Pin your strongest work so visitors can find it quickly.</p>
                  )}
                </div>
                <div className="profile-signal-section">
                  <h3>Primary repository languages</h3>
                  <div className="profile-language-list">
                    {(quality.profile_level?.languages || []).length ? (
                      quality.profile_level.languages.map((language) => <span key={language}>{language}</span>)
                    ) : <span>None detected</span>}
                  </div>
                </div>
                <div className="profile-signal-section">
                  <h3>Strengths</h3>
                  {(quality.profile_level?.strengths || []).length ? (
                    quality.profile_level.strengths.map((item, index) => <p className="reason-earned" key={index}>+ {item}</p>)
                  ) : <p className="hygiene-neutral">No strong profile signals were verified yet.</p>}
                </div>
                <div className="profile-signal-section">
                  <h3>What to improve</h3>
                  {(quality.profile_level?.improvements || []).map((item, index) => <p className="reason-missing" key={index}>− {item}</p>)}
                </div>
                <p className="profile-data-note">{quality.profile_level?.note}</p>
              </fieldset>
              </div>
            </div>
          )}
        </div>
      </main>
    </>
  );
}

export default Home;
