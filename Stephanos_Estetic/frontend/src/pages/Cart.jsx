import { useCart } from "../context/CartContext.jsx";
import { Trash2, Plus, Minus } from "lucide-react";

export default function Cart() {
  const { items, updateQty, removeItem, clearCart, subtotal } = useCart();

  const shipping = subtotal > 50000 || subtotal === 0 ? 0 : 3990; // ejemplo
  const total = subtotal + shipping;

  if (items.length === 0) {
    return (
      <section className="min-h-[60vh] bg-gradient-to-b from-white to-pink-50">
        <div className="site-container py-16 text-center">
          <h1 className="text-3xl font-bold">Tu carrito</h1>
          <p className="text-gray-600 mt-2">Aún no has agregado productos.</p>
        </div>
      </section>
    );
  }

  async function handleCheckout() {
    if (items.length === 0) return;

    // Construye el payload como espera el backend: [{ sku, qty }]
    // Si tu carrito no tiene `sku`, usamos `id` (porque arriba lo cargas como id=sku).
    const payload = {
      items: items.map((it) => ({
        sku: it.sku || it.id, // <-- clave
        qty: Math.max(1, Number(it.qty) || 1),
      })),
      // opcional:
      // customer_name: "",
      // customer_email: "",
    };

    try {
      const res = await fetch("/api/checkout/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // Idempotencia simple (evita doble click): no usa crypto.randomUUID
          "Idempotency-Key": String(Date.now()),
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        // Mensajes de validación del backend (stock insuficiente, SKU inexistente, etc.)
        const msg =
          Array.isArray(data?.errors) && data.errors.length
            ? data.errors.join("\n")
            : data?.detail || `Error HTTP ${res.status}`;
        alert(msg);
        return;
      }

      alert(`Orden #${data.order_id} creada. Total: $${data.total_amount}`);
      clearCart();
      // (opcional) redirige a una página de éxito
      // navigate(`/order-success?id=${data.order_id}`);
    } catch (err) {
      alert(err?.message || "Error de red");
    }
  }

  return (
    <section className="min-h-screen bg-gradient-to-b from-white to-pink-50 py-8">
      <div className="site-container grid lg:grid-cols-3 gap-8">
        {/* Lista */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-gray-100 shadow-sm">
          <div className="p-6 flex items-center justify-between">
            <h1 className="text-2xl font-bold">Tu carrito</h1>
            <button
              onClick={clearCart}
              className="text-sm text-pink-600 hover:text-pink-700 font-semibold"
            >
              Vaciar carrito
            </button>
          </div>

          <div className="divide-y">
            {items.map((it) => (
              <div key={it.id} className="p-6 flex gap-4 items-center">
                <div className="h-20 w-24 rounded-lg bg-pink-50 overflow-hidden flex items-center justify-center">
                  {it.image_url ? (
                    <img
                      src={it.image_url}
                      alt={it.name}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <span className="text-3xl">🛍️</span>
                  )}
                </div>

                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{it.name}</h3>
                  {it.category && (
                    <span className="text-xs inline-block mt-1 px-2 py-0.5 rounded-full bg-pink-100 text-pink-600">
                      {labelize(it.category)}
                    </span>
                  )}
                  <div className="mt-3 flex items-center gap-2">
                    <button
                      onClick={() => updateQty(it.id, it.qty - 1)}
                      className="h-8 w-8 rounded-md border border-gray-300 flex items-center justify-center hover:bg-gray-50"
                    >
                      <Minus className="h-4 w-4" />
                    </button>
                    <input
                      type="number"
                      min="1"
                      value={it.qty}
                      onChange={(e) =>
                        updateQty(it.id, parseInt(e.target.value || "1", 10))
                      }
                      className="w-14 text-center rounded-md border border-gray-300 py-1"
                    />
                    <button
                      onClick={() => updateQty(it.id, it.qty + 1)}
                      className="h-8 w-8 rounded-md border border-gray-300 flex items-center justify-center hover:bg-gray-50"
                    >
                      <Plus className="h-4 w-4" />
                    </button>

                    <button
                      onClick={() => removeItem(it.id)}
                      className="ml-3 inline-flex items-center gap-1 text-red-600 hover:text-red-700 text-sm"
                    >
                      <Trash2 className="h-4 w-4" />
                      Quitar
                    </button>
                  </div>
                </div>

                <div className="text-right">
                  <div className="font-semibold text-gray-900">
                    {formatPrice(it.price)}
                  </div>
                  <div className="text-sm text-gray-500">
                    Subtotal: {formatPrice(it.price * it.qty)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Resumen */}
        <aside className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 h-fit">
          <h2 className="text-xl font-bold">Resumen</h2>
          <div className="mt-4 space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Subtotal</span>
              <span>{formatPrice(subtotal)}</span>
            </div>
            <div className="flex justify-between">
              <span>Envío</span>
              <span>{shipping === 0 ? "Gratis" : formatPrice(shipping)}</span>
            </div>
            <div className="h-px bg-gray-200 my-2" />
            <div className="flex justify-between text-base font-semibold">
              <span>Total</span>
              <span>{formatPrice(total)}</span>
            </div>
          </div>

          <button
            onClick={handleCheckout}
            className="mt-6 w-full px-6 py-3 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all"
          >
            Ir a pagar
          </button>

          <p className="text-xs text-gray-500 mt-3">
            Al continuar aceptas nuestros Términos y Política de privacidad.
          </p>
        </aside>
      </div>
    </section>
  );
}

function formatPrice(n) {
  if (typeof n !== "number") return n ?? "";
  try {
    return new Intl.NumberFormat("es-CL", {
      style: "currency",
      currency: "CLP",
      maximumFractionDigits: 0,
    }).format(n);
  } catch {
    return `$${n}`;
  }
}
function labelize(s) {
  return String(s || "")
    .replace(/[_-]/g, " ")
    .replace(/\b\w/g, (m) => m.toUpperCase());
}
