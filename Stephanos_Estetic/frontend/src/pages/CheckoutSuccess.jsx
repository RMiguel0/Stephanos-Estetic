import { useEffect, useState } from "react";

export default function CheckoutSuccess() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const params = new URLSearchParams(window.location.search);
  const ok = params.get("ok") === "true";
  const buyOrder = params.get("buy_order");

  useEffect(() => {
    async function load() {
      if (!buyOrder) { setLoading(false); return; }
      try {
        const r = await fetch(`http://localhost:8000/api/payments/detail?buy_order=${encodeURIComponent(buyOrder)}`);
        const j = await r.json();
        setData(j);
      } finally { setLoading(false); }
    }
    load();
  }, [buyOrder]);

  if (!ok) {
    return (
      <section className="site-container py-16">
        <h1 className="text-2xl font-bold text-red-600 mb-4">Pago rechazado o cancelado</h1>
        <p className="text-gray-600">Si crees que es un error, intenta nuevamente.</p>
      </section>
    );
  }

  return (
    <section className="site-container py-16">
      <h1 className="text-3xl font-bold mb-6">¡Compra exitosa! 🎉</h1>

      {loading && <p>Cargando detalles…</p>}

      {data && (
        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm max-w-2xl">
          <div className="grid grid-cols-2 gap-y-2 text-sm">
            <span className="text-gray-500">Orden</span>
            <span className="font-medium">{data.buy_order}</span>

            <span className="text-gray-500">Estado</span>
            <span className="font-medium">{data.status}</span>

            <span className="text-gray-500">Monto</span>
            <span className="font-medium">${Number(data.amount).toLocaleString("es-CL")}</span>

            {data.authorization_code && (
              <>
                <span className="text-gray-500">Autorización</span>
                <span className="font-medium">{data.authorization_code}</span>
              </>
            )}
            {data.transaction_date && (
              <>
                <span className="text-gray-500">Fecha</span>
                <span className="font-medium">{new Date(data.transaction_date).toLocaleString("es-CL")}</span>
              </>
            )}
          </div>

          <a
            href={`http://localhost:8000/api/payments/receipt?buy_order=${encodeURIComponent(buyOrder)}`}
            className="mt-6 inline-flex items-center justify-center px-4 py-2 rounded-lg bg-pink-600 text-white font-semibold hover:bg-pink-700"
          >
            Descargar boleta (PDF)
          </a>
        </div>
      )}
    </section>
  );
}
