const API_BASE = import.meta.env.VITE_API_BASE || "";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  health: () => request("/api/health"),
  presets: () => request("/api/presets"),
  searchLocations: (query) =>
    request(`/api/locations/search?q=${encodeURIComponent(query)}`),
  reverseLocation: (latitude, longitude) =>
    request(
      `/api/locations/reverse?latitude=${encodeURIComponent(latitude)}&longitude=${encodeURIComponent(longitude)}`
    ),
  calibrate: (body) =>
    request("/api/calibrate", { method: "POST", body: JSON.stringify(body) }),
  simulate: (body) =>
    request("/api/calibrate/simulate", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  analytics: () => request("/api/analytics?limit=30"),
};
