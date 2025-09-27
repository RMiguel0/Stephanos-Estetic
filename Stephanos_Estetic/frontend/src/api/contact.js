const API_BASE = import.meta.env.VITE_API_BASE || '/api'

export const ContactAPI = {
  submit: (payload) =>
    fetch(`${API_BASE}/contact/requests/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(async (r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      try { return await r.json() } catch { return null }
    }),
}
