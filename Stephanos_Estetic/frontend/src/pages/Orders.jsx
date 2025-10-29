import { useState, useEffect } from "react";
import { Calendar, Package, AlertCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";

// misma base que en UserProfile.jsx
const API_BASE =
  window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "http://localhost:8000";

export default function Orders({ onNavigate }) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const goToServices = () => {
    if (onNavigate) {
      onNavigate("services"); // si te pasan el prop, úsalo
    } else {
      navigate("/services"); // si no, navega con react-router
    }
  };

  useEffect(() => {
    async function fetchOrders() {
      setError("");
      try {
        // primero valida sesión
        const meRes = await fetch(`${API_BASE}/api/user/me/`, {
          credentials: "include",
        });
        const me = await meRes.json();
        if (!me?.is_authenticated) {
          // sin sesión -> redirige a login
          window.location.href = `${API_BASE.replace(
            /\/$/,
            ""
          )}/accounts/google/login/`;
          return;
        }

        // luego carga órdenes
        const res = await fetch(`${API_BASE}/api/orders/`, {
          credentials: "include",
        });
        if (!res.ok) throw new Error("Error al cargar órdenes");
        const data = await res.json();
        setOrders(data.orders || []);
      } catch (err) {
        console.error(err);
        setError("No se pudieron cargar tus órdenes.");
      } finally {
        setLoading(false);
      }
    }

    fetchOrders();
  }, []);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("es-CL", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-pink-50 py-12">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Mis{" "}
            <span className="bg-gradient-to-r from-pink-500 to-pink-600 bg-clip-text text-transparent">
              Órdenes
            </span>
          </h1>
          <p className="text-gray-600">
            Revisa tus compras o contrataciones de servicios
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
            <AlertCircle className="h-5 w-5 text-red-600 mr-2 mt-0.5 flex-shrink-0" />
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {orders.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-sm p-12 text-center border border-gray-100">
            <Package className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No hay órdenes aún
            </h3>
            <p className="text-gray-600 mb-6">
              Aún no has realizado compras ni contrataciones. ¡Explora nuestros
              servicios y haz tu primera reserva o pedido!
            </p>
            <button
              onClick={goToServices}
              className="px-6 py-3 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all"
            >
              Explorar servicios
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {orders.map((o) => (
              <div
                key={o.order_id}
                className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all"
              >
                <div className="p-6">
                  <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-4">
                    <div className="mb-4 lg:mb-0">
                      <h3 className="text-xl font-bold text-gray-900 mb-1">
                        Orden #{o.order_id}
                      </h3>
                      <p className="text-sm text-gray-500">
                        Cliente: {o.customer_name || "—"}
                      </p>
                      <p className="text-sm text-gray-500">
                        Email: {o.customer_email || "—"}
                      </p>
                    </div>
                    <div className="text-left lg:text-right">
                      <div className="text-2xl font-bold text-pink-600">
                        ${o.total_amount.toFixed(0)}
                      </div>
                      <div className="text-sm text-gray-500">
                        Realizada el {formatDate(o.created_at)}
                      </div>
                    </div>
                  </div>

                  {/* Detalle de ítems */}
                  {o.items && o.items.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-gray-100">
                      <h4 className="text-sm font-semibold text-gray-700 mb-2">
                        Productos / Servicios
                      </h4>
                      <ul className="divide-y divide-gray-100">
                        {o.items.map((item, idx) => (
                          <li
                            key={idx}
                            className="py-2 flex justify-between text-sm text-gray-700"
                          >
                            <span>
                              {item.product} x{item.qty}
                            </span>
                            <span>${item.line_total.toFixed(0)}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <div className="flex items-start">
                      <Calendar className="h-5 w-5 text-pink-500 mr-3 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="text-sm font-medium text-gray-500">
                          Última actualización
                        </p>
                        <p className="text-gray-900">
                          {formatDate(o.viewed_at)}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-8 bg-gradient-to-r from-pink-500 to-pink-600 rounded-2xl p-8 text-center text-white shadow-lg">
          <h3 className="text-2xl font-bold mb-3">
            ¿Necesitas ayuda con tu pedido?
          </h3>
          <p className="text-pink-100 mb-6">
            Si tienes dudas o necesitas asistencia con una orden, contáctanos.
          </p>
          <button
            onClick={() => onNavigate && onNavigate("contact")}
            className="px-6 py-3 bg-white text-pink-600 rounded-lg font-semibold hover:bg-pink-50 transition-all"
          >
            Contactar soporte
          </button>
        </div>
      </div>
    </div>
  );
}
