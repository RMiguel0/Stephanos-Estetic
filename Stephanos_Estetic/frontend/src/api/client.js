const API_BASE = import.meta.env.VITE_API_BASE || '/api'

async function http(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`HTTP ${res.status} ${res.statusText} ${text}`)
  }
  // intenta parsear JSON; si no hay body, devuelve null
  try { return await res.json() } catch { return null }
}

export const api = {
  get: (path) => http(path),
  post: (path, body) => http(path, { method: 'POST', body: JSON.stringify(body) }),
  // agrega put/patch/delete si lo necesitas
}
