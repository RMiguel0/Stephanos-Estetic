import { useEffect, useRef, useState } from 'react'
import { ContactAPI } from '../api/contact'

export default function ContactPage() {
  const [sentAt, setSentAt] = useState(0)
  const [ok, setOk] = useState(false)
  const [err, setErr] = useState(null)
  const websiteRef = useRef(null) // honeypot

  useEffect(() => {
    setSentAt(Math.floor(Date.now() / 1000))
  }, [])

  async function onSubmit(e) {
    e.preventDefault()
    const form = new FormData(e.currentTarget)
    const payload = {
      name: form.get('name'),
      email: form.get('email'),
      phone: form.get('phone') || '',
      message: form.get('message'),
      website: websiteRef.current?.value || '', // honeypot
      sent_at: sentAt,
    }
    try {
      await ContactAPI.submit(payload)
      setOk(true); setErr(null); e.currentTarget.reset()
    } catch (error) {
      setErr(error.message); setOk(false)
    }
  }

  return (
    <section style={{ padding: 24, maxWidth: 720, margin: '0 auto' }}>
      <h2>Contacto</h2>
      {ok && <p style={{ color: 'green' }}>¡Gracias! Te contactaremos pronto.</p>}
      {err && <p style={{ color: 'red' }}>Error: {err}</p>}

      <form onSubmit={onSubmit}>
        <div style={{ display: 'grid', gap: 12 }}>
          <input name="name" placeholder="Nombre" required />
          <input name="email" type="email" placeholder="Email" required />
          <input name="phone" placeholder="Teléfono (opcional)" />
          <textarea name="message" placeholder="Mensaje" rows={5} required />

          {/* Honeypot oculto para bots */}
          <input
            ref={websiteRef}
            name="website"
            style={{ display: 'none' }}
            tabIndex={-1}
            autoComplete="off"
          />

          <button type="submit">Enviar</button>
        </div>
      </form>
    </section>
  )
}
