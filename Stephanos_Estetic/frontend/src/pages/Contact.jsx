import { useState } from "react";

export default function Contact() {
  const [status, setStatus] = useState(null);

  async function onSubmit(e) {
    e.preventDefault();
    const payload = Object.fromEntries(new FormData(e.currentTarget).entries());
    try {
      const res = await fetch("/api/contact/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("Error al enviar");
      setStatus("ok");
      e.currentTarget.reset();
    } catch {
      setStatus("error");
    }
  }

  return (
    <section className="site-container max-w-xl">
      <h1 className="text-3xl font-bold">Contacto / Reserva</h1>
      <p className="text-gray-600 mt-2">Déjanos tus datos y te confirmamos disponibilidad.</p>

      <form onSubmit={onSubmit} className="mt-6 space-y-4">
        <div>
          <label className="block text-sm mb-1">Nombre</label>
          <input name="name" required className="w-full rounded-md border border-gray-300 px-3 py-2 outline-none focus:ring-2 focus:ring-emerald-500" />
        </div>
        <div>
          <label className="block text-sm mb-1">Email</label>
          <input name="email" type="email" required className="w-full rounded-md border border-gray-300 px-3 py-2 outline-none focus:ring-2 focus:ring-emerald-500" />
        </div>
        <div>
          <label className="block text-sm mb-1">Mensaje</label>
          <textarea name="message" rows="4" className="w-full rounded-md border border-gray-300 px-3 py-2 outline-none focus:ring-2 focus:ring-emerald-500" />
        </div>
        <button className="btn-primary">Enviar</button>

        {status === "ok" && (
          <p className="text-emerald-700 bg-emerald-50 px-3 py-2 rounded-md text-sm">¡Mensaje enviado!</p>
        )}
        {status === "error" && (
          <p className="text-red-700 bg-red-50 px-3 py-2 rounded-md text-sm">Algo falló, intenta de nuevo.</p>
        )}
      </form>
    </section>
  );
}
