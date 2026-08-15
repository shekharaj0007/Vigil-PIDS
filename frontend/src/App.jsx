import { lazy, Suspense, useEffect, useRef, useState } from "react";
import { api } from "./api";

const RiskTrendChart = lazy(() => import("./RiskTrendChart"));

const SCENARIOS = [
  {
    label: "Calm / Clear",
    data: {
      location_name: "Demo — Calm Perimeter",
      latitude: 28.61,
      longitude: 77.21,
      temperature_c: 28,
      humidity_pct: 45,
      wind_speed_kmh: 8,
      rainfall_mm: 0,
      weather_code: 0,
      weather_label: "Clear sky",
      is_storm: false,
      recorded_at: new Date().toISOString(),
    },
  },
  {
    label: "High Wind",
    data: {
      location_name: "Demo — Windy Fence Line",
      latitude: 19.07,
      longitude: 72.87,
      temperature_c: 31,
      humidity_pct: 55,
      wind_speed_kmh: 48,
      rainfall_mm: 0,
      weather_code: 3,
      weather_label: "Overcast",
      is_storm: false,
      recorded_at: new Date().toISOString(),
    },
  },
  {
    label: "Heavy Rain",
    data: {
      location_name: "Demo — Rain Zone",
      latitude: 12.97,
      longitude: 77.59,
      temperature_c: 24,
      humidity_pct: 88,
      wind_speed_kmh: 18,
      rainfall_mm: 8,
      weather_code: 65,
      weather_label: "Heavy rain",
      is_storm: false,
      recorded_at: new Date().toISOString(),
    },
  },
  {
    label: "Thunderstorm",
    data: {
      location_name: "Demo — Storm Sector",
      latitude: 22.57,
      longitude: 88.36,
      temperature_c: 26,
      humidity_pct: 92,
      wind_speed_kmh: 55,
      rainfall_mm: 12,
      weather_code: 95,
      weather_label: "Thunderstorm",
      is_storm: true,
      recorded_at: new Date().toISOString(),
    },
  },
];

function badgeClass(level) {
  return `badge badge-${String(level).toLowerCase().replace(/\s+/g, "-")}`;
}

export default function App() {
  const [online, setOnline] = useState(false);
  const [presets, setPresets] = useState([]);
  const [preset, setPreset] = useState("");
  const [locationName, setLocationName] = useState("New Delhi");
  const [latitude, setLatitude] = useState(28.6139);
  const [longitude, setLongitude] = useState(77.209);
  const [placeQuery, setPlaceQuery] = useState("");
  const [placeResults, setPlaceResults] = useState([]);
  const [findingPlace, setFindingPlace] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const reverseRequest = useRef(0);

  async function refreshAnalytics() {
    try {
      const data = await api.analytics();
      setAnalytics(data);
    } catch {
      /* ignore until first run */
    }
  }

  useEffect(() => {
    (async () => {
      try {
        await api.health();
        setOnline(true);
        const list = await api.presets();
        setPresets(list);
        if (list[0]) {
          setPreset(list[0].name);
          setLocationName(list[0].name);
          setLatitude(list[0].latitude);
          setLongitude(list[0].longitude);
        }
        await refreshAnalytics();
      } catch {
        setOnline(false);
      }
    })();
  }, []);

  useEffect(() => {
    const lat = Number(latitude);
    const lon = Number(longitude);
    if (!online || !Number.isFinite(lat) || !Number.isFinite(lon)) return;
    if (lat < -90 || lat > 90 || lon < -180 || lon > 180) return;

    const requestId = ++reverseRequest.current;
    const timer = setTimeout(async () => {
      setFindingPlace(true);
      try {
        const location = await api.reverseLocation(lat, lon);
        if (requestId === reverseRequest.current) setLocationName(location.name);
      } catch {
        if (requestId === reverseRequest.current) {
          setLocationName(`${lat.toFixed(4)}, ${lon.toFixed(4)}`);
        }
      } finally {
        if (requestId === reverseRequest.current) setFindingPlace(false);
      }
    }, 900);

    return () => clearTimeout(timer);
  }, [latitude, longitude, online]);

  function onPresetChange(name) {
    setPreset(name);
    const found = presets.find((p) => p.name === name);
    if (found) {
      setLocationName(found.name);
      setLatitude(found.latitude);
      setLongitude(found.longitude);
    }
  }

  async function findLocations(event) {
    event.preventDefault();
    if (placeQuery.trim().length < 2) return;
    setFindingPlace(true);
    setError("");
    try {
      setPlaceResults(await api.searchLocations(placeQuery.trim()));
    } catch (err) {
      setError(err.message);
    } finally {
      setFindingPlace(false);
    }
  }

  function chooseLocation(location) {
    reverseRequest.current += 1;
    setPreset("");
    setLocationName(location.name);
    setLatitude(location.latitude);
    setLongitude(location.longitude);
    setPlaceQuery(location.name);
    setPlaceResults([]);
  }

  async function runLive() {
    setLoading(true);
    setError("");
    try {
      const data = await api.calibrate({
        latitude: Number(latitude),
        longitude: Number(longitude),
        location_name: locationName,
      });
      setResult(data);
      await refreshAnalytics();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function runScenario(scenario) {
    setLoading(true);
    setError("");
    try {
      const data = await api.simulate(scenario.data);
      setResult(data);
      await refreshAnalytics();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const weather = result?.weather;
  const rec = result?.recommendation;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            Vigil <span>PIDS</span>
          </div>
          <p className="brand-sub">
            Weather-based sensor calibration suggestions to cut environmental false alarms.
          </p>
        </div>
        <div className="status-chip">
          <span className={`status-dot ${online ? "" : "offline"}`} />
          {online ? "API online" : "API offline — start backend"}
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="grid-main">
        <section className="panel">
          <h2 className="section-title">Operator controls</h2>
          <div className="controls">
            <form className="location-search" onSubmit={findLocations}>
              <div className="field">
                <label>Search any location worldwide</label>
                <input
                  value={placeQuery}
                  onChange={(e) => setPlaceQuery(e.target.value)}
                  placeholder="City, district, landmark or address"
                />
              </div>
              <button className="btn btn-ghost" disabled={!online || findingPlace}>
                {findingPlace ? "Finding…" : "Search"}
              </button>
            </form>
            {placeResults.length > 0 && (
              <div className="location-results">
                {placeResults.map((location) => (
                  <button
                    type="button"
                    key={`${location.latitude}-${location.longitude}`}
                    onClick={() => chooseLocation(location)}
                  >
                    <strong>{location.name}</strong>
                    <span>{location.display_name}</span>
                  </button>
                ))}
              </div>
            )}
            <div className="field">
              <label>Quick site preset</label>
              <select value={preset} onChange={(e) => onPresetChange(e.target.value)}>
                <option value="">Custom / any location</option>
                {presets.map((p) => (
                  <option key={p.name} value={p.name}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>{findingPlace ? "Detecting place…" : "Detected location name"}</label>
              <input
                value={locationName}
                onChange={(e) => setLocationName(e.target.value)}
              />
            </div>
            <div className="row-2">
              <div className="field">
                <label>Latitude</label>
                <input
                  type="number"
                  step="0.0001"
                  value={latitude}
                  onChange={(e) => {
                    setPreset("");
                    setLatitude(e.target.value);
                  }}
                />
              </div>
              <div className="field">
                <label>Longitude</label>
                <input
                  type="number"
                  step="0.0001"
                  value={longitude}
                  onChange={(e) => {
                    setPreset("");
                    setLongitude(e.target.value);
                  }}
                />
              </div>
            </div>
            <div className="btn-row">
              <button className="btn btn-primary" disabled={loading || !online} onClick={runLive}>
                {loading ? "Analyzing…" : "Fetch weather & recommend"}
              </button>
              <button
                className="btn btn-ghost"
                disabled={loading || !online}
                onClick={refreshAnalytics}
              >
                Refresh analytics
              </button>
            </div>
            <div>
              <label style={{ fontSize: "0.8rem", color: "var(--muted)" }}>
                Demo scenarios (offline sample conditions)
              </label>
              <div className="scenarios">
                {SCENARIOS.map((s) => (
                  <button
                    key={s.label}
                    className="scenario-btn"
                    disabled={loading || !online}
                    onClick={() => runScenario(s)}
                  >
                    {s.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="panel">
          <h2 className="section-title">Calibration recommendation</h2>
          {!rec ? (
            <p className="empty">
              Select a site and run live analysis, or try a demo scenario to see sensitivity
              guidance.
            </p>
          ) : (
            <>
              <div className="rec-hero">
                <div style={{ opacity: 0.8, fontSize: "0.85rem" }}>Recommended sensitivity</div>
                <div className="rec-level">{rec.sensitivity_level}</div>
                <div className="rec-score">
                  <strong>{rec.sensitivity_score}</strong>
                  <span>/ 100</span>
                  <span style={{ marginLeft: "auto", opacity: 0.85 }}>
                    Risk {(rec.risk_score * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="rationale">{rec.rationale}</p>
              </div>
              <h3 className="section-title" style={{ fontSize: "1rem" }}>
                Operator actions
              </h3>
              <ul className="actions">
                {rec.action_items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
              <div className="factors">
                {Object.entries(rec.factor_breakdown || {}).map(([key, val]) => (
                  <div className="factor-row" key={key}>
                    <span style={{ textTransform: "capitalize" }}>{key}</span>
                    <div className="bar-track">
                      <div
                        className="bar-fill"
                        style={{ width: `${Math.round(val.impact * 100)}%` }}
                      />
                    </div>
                    <span style={{ color: "var(--muted)" }}>
                      {(val.impact * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>
            </>
          )}
        </section>
      </div>

      <section className="panel" style={{ marginBottom: "1.1rem" }}>
        <h2 className="section-title">Live weather parameters</h2>
        {!weather ? (
          <p className="empty">Weather metrics appear after a calibration run.</p>
        ) : (
          <div className="metric-grid">
            <div className="metric">
              <div className="metric-label">Temperature</div>
              <div className="metric-value">{weather.temperature_c.toFixed(1)}°C</div>
            </div>
            <div className="metric">
              <div className="metric-label">Humidity</div>
              <div className="metric-value">{weather.humidity_pct.toFixed(0)}%</div>
            </div>
            <div className="metric">
              <div className="metric-label">Wind speed</div>
              <div className="metric-value">{weather.wind_speed_kmh.toFixed(1)} km/h</div>
            </div>
            <div className="metric">
              <div className="metric-label">Rainfall</div>
              <div className="metric-value">{weather.rainfall_mm.toFixed(1)} mm</div>
            </div>
            <div className="metric">
              <div className="metric-label">Condition</div>
              <div className="metric-value" style={{ fontSize: "1.05rem" }}>
                {weather.weather_label}
              </div>
            </div>
            <div className="metric">
              <div className="metric-label">Storm</div>
              <div className="metric-value">{weather.is_storm ? "Yes" : "No"}</div>
            </div>
          </div>
        )}
      </section>

      <div className="grid-lower">
        <section className="panel">
          <h2 className="section-title">Analytics overview</h2>
          {!analytics || analytics.total_recommendations === 0 ? (
            <p className="empty">Run calibrations to populate reports.</p>
          ) : (
            <>
              <div className="stat-strip">
                <div className="stat">
                  <span style={{ color: "var(--muted)", fontSize: "0.8rem" }}>Runs</span>
                  <strong>{analytics.total_recommendations}</strong>
                </div>
                <div className="stat">
                  <span style={{ color: "var(--muted)", fontSize: "0.8rem" }}>Avg risk</span>
                  <strong>{(analytics.avg_risk_score * 100).toFixed(0)}%</strong>
                </div>
                <div className="stat">
                  <span style={{ color: "var(--muted)", fontSize: "0.8rem" }}>Storms</span>
                  <strong>{analytics.storm_events}</strong>
                </div>
                <div className="stat">
                  <span style={{ color: "var(--muted)", fontSize: "0.8rem" }}>Avg wind</span>
                  <strong>{analytics.avg_wind_speed} km/h</strong>
                </div>
              </div>
              <div className="chart-box">
                <Suspense fallback={<p className="empty">Loading chart…</p>}>
                  <RiskTrendChart data={analytics.risk_trend} />
                </Suspense>
              </div>
              <p style={{ color: "var(--muted)", fontSize: "0.8rem", marginTop: "0.5rem" }}>
                Sensitivity distribution:{" "}
                {Object.entries(analytics.sensitivity_distribution)
                  .map(([k, v]) => `${k} (${v})`)
                  .join(" · ") || "—"}
              </p>
            </>
          )}
        </section>

        <section className="panel">
          <h2 className="section-title">Recommendation history</h2>
          {!analytics?.recent_history?.length ? (
            <p className="empty">No history yet.</p>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Site</th>
                    <th>Weather</th>
                    <th>Wind</th>
                    <th>Rain</th>
                    <th>Sensitivity</th>
                    <th>Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {analytics.recent_history.map((row) => (
                    <tr key={row.id}>
                      <td>{row.location_name}</td>
                      <td>{row.weather_label}</td>
                      <td>{row.wind_speed_kmh.toFixed(0)}</td>
                      <td>{row.rainfall_mm.toFixed(1)}</td>
                      <td>
                        <span className={badgeClass(row.sensitivity_level)}>
                          {row.sensitivity_level}
                        </span>
                      </td>
                      <td>{(row.risk_score * 100).toFixed(0)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
