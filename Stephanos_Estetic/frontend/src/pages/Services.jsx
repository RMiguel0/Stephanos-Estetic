import { useState, useEffect } from "react";
import { Clock, DollarSign, Calendar, Check, X } from "lucide-react";

// importa todas las imágenes de la carpeta como URLs procesadas por Vite
const serviceImages = import.meta.glob(
  "../assets/services/*.{webp,png,jpg,jpeg,svg}",
  { eager: true, import: "default" }
);

// util: genera slug consistente a partir del nombre si no tienes service.slug
function toSlug(text = "") {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "") // quita tildes
    .replace(/[^a-z0-9\s-]/g, "")
    .trim()
    .replace(/\s+/g, "-");
}

function getServiceImage(service) {
  if (!service) return null;

  const baseName =
    (service.slug && String(service.slug).trim()) ||
    (service.name && toSlug(service.name)) ||
    "";

  if (!baseName) return null;

  const candidates = [
    `../assets/services/${baseName}.webp`,
    `../assets/services/${baseName}.jpg`,
    `../assets/services/${baseName}.jpeg`,
    `../assets/services/${baseName}.png`,
    `../assets/services/${baseName}.svg`,
  ];
  for (const p of candidates) {
    if (serviceImages[p]) return serviceImages[p];
  }
  return null; // fuerza el fallback a emoji
}

export default function Services() {
  const [services, setServices] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [selectedService, setSelectedService] = useState(null);
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  const [loading, setLoading] = useState(true);
  const [bookingForm, setBookingForm] = useState({
    customer_name: "",
    customer_email: "",
    customer_phone: "",
    notes: "",
  });
  const [showSuccess, setShowSuccess] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchServices();
  }, []);

  useEffect(() => {
    if (selectedService) {
      fetchSchedules(selectedService.id); // puede ser numérico o "svcX", el backend acepta ambos
    }
  }, [selectedService]);

  const fetchJSON = async (url) => {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  };

  const fetchServices = async () => {
    setLoading(true);
    try {
      const data = await fetchJSON("/api/services/?active=true");
      setServices(Array.isArray(data) ? data.filter(Boolean) : []);
    } catch (err) {
      console.warn("GET /api/services fallback:", err?.message);
      setServices([
        {
          id: "svc1",
          type: "beauty",
          name: "Limpieza facial profunda",
          description:
            "Renueva y oxigena tu piel con una limpieza profesional.",
          duration_minutes: 60,
          price: 24990,
          active: true,
        },
        {
          id: "svc2",
          type: "coaching",
          name: "Masoterapia descontracturante",
          description: "Alivia tensiones y mejora tu descanso.",
          duration_minutes: 50,
          price: 22990,
          active: true,
        },
        {
          id: "svc3",
          type: "beauty",
          name: "Peeling químico",
          description: "Mejora textura y luminosidad de tu piel.",
          duration_minutes: 45,
          price: 34990,
          active: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const fetchSchedules = async (serviceId) => {
    try {
      // RANGO: hoy -> +14 días
      const from = new Date();
      const to = new Date(from);
      to.setDate(to.getDate() + 14);

      const dateFrom = from.toISOString().slice(0, 10);
      const dateTo = to.toISOString().slice(0, 10);

      const url = `/api/service_schedules/?service_id=${encodeURIComponent(
        serviceId
      )}&is_booked=false&date_from=${dateFrom}&date_to=${dateTo}`;

      const data = await fetchJSON(url);

      // Soporta array plano o { items: [...] }
      const raw = Array.isArray(data) ? data : data?.items ?? [];

      // Normaliza a { id, service_id, date, start_time, is_booked }
      let normalized = raw.map((s) => {
        const iso = s.starts_at ?? s.start;
        const d = new Date(iso);
        const date = d.toISOString().slice(0, 10);
        const hh = String(d.getHours()).padStart(2, "0");
        const mm = String(d.getMinutes()).padStart(2, "0");
        return {
          id: s.id,
          service_id: s.service_id ?? serviceId,
          date,
          start_time: `${hh}:${mm}`,
          is_booked: (s.is_booked ?? s.isBooked) === true,
        };
      });

      // Segundo intento opcional si estás probando una fecha fija
      if (normalized.length === 0) {
        const forceDate = "2025-10-20";
        const forceUrl = `/api/service_schedules/?service_id=${encodeURIComponent(
          serviceId
        )}&is_booked=false&date_from=${forceDate}`;

        const data2 = await fetchJSON(forceUrl);
        const raw2 = Array.isArray(data2) ? data2 : data2?.items ?? [];
        normalized = raw2.map((s) => {
          const iso = s.starts_at ?? s.start;
          const d = new Date(iso);
          const date = d.toISOString().slice(0, 10);
          const hh = String(d.getHours()).padStart(2, "0");
          const mm = String(d.getMinutes()).padStart(2, "0");
          return {
            id: s.id,
            service_id: s.service_id ?? serviceId,
            date,
            start_time: `${hh}:${mm}`,
            is_booked: (s.is_booked ?? s.isBooked) === true,
          };
        });
      }

      setSchedules(normalized);
    } catch (err) {
      console.error("Error schedules:", err);
      setSchedules([]);
    }
  };

  // util chico para CSRF desde cookie (Django)
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
  }

  const handleBooking = async (e) => {
    e.preventDefault();
    if (!selectedSchedule) return;
    setError("");

    const booking = {
      service_schedule_id: selectedSchedule.id,
      customer_name: bookingForm.customer_name,
      customer_email: bookingForm.customer_email,
      customer_phone: bookingForm.customer_phone,
      notes: bookingForm.notes,
    };

    try {
      await fetch("/api/csrf/", { credentials: "include" });
      const res = await fetch("/api/bookings/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken") || "",
        },
        body: JSON.stringify(booking),
        credentials: "include",
      });

      if (!res.ok) {
        const msg = await res.text();
        throw new Error(msg || `HTTP ${res.status}`);
      }

      setShowSuccess(true);
      setBookingForm({
        customer_name: "",
        customer_email: "",
        customer_phone: "",
        notes: "",
      });
      setSelectedSchedule(null);
      if (selectedService) fetchSchedules(selectedService.id); // refresca la grilla

      setTimeout(() => {
        setShowSuccess(false);
        setSelectedService(null);
      }, 2500);
    } catch (err) {
      console.error("booking error:", err);
      setError(
        typeof err?.message === "string"
          ? err.message
          : "No se pudo crear la reserva."
      );
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString + "T00:00:00");
    return date.toLocaleDateString("es-CL", {
      weekday: "long",
      month: "long",
      day: "numeric",
    });
  };

  const formatTime = (timeString) => {
    const [hours, minutes] = timeString.split(":");
    const hour = parseInt(hours, 10);
    const ampm = hour >= 12 ? "PM" : "AM";
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-pink-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            Nuestros{" "}
            <span className="bg-gradient-to-r from-pink-500 to-pink-600 bg-clip-text text-transparent">
              Servicios
            </span>
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Reserva tu sesión de coaching o belleza personalizada con nuestro
            equipo de expertos
          </p>
        </div>

        {/* Listado de servicios */}
        {!selectedService ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {services.map((service) => (
              <div
                key={service.id}
                className="bg-white rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100 hover:-translate-y-1 cursor-pointer"
                onClick={() => setSelectedService(service)}
              >
                {/* IMAGEN en vez de emoji */}
                <div className="h-48 bg-gray-50 flex items-center justify-center relative">
                  {getServiceImage(service) ? (
                    <img
                      src={getServiceImage(service)}
                      alt={service?.name || "Servicio"}
                      loading="lazy"
                      className="absolute inset-0 w-full h-full object-cover"
                      sizes="(max-width: 768px) 100vw, 33vw"
                    />
                  ) : (
                    <div className="text-6xl">
                      {service?.type === "coaching" ? "🎯" : "💆‍♀️"}
                    </div>
                  )}
                </div>

                <div className="p-6">
                  <div className="inline-block px-3 py-1 bg-pink-100 text-pink-600 rounded-full text-xs font-semibold mb-3 uppercase">
                    {service?.type || "servicio"}
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {service?.name}
                  </h3>
                  <p className="text-gray-600 mb-4 line-clamp-2">
                    {service?.description}
                  </p>
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center text-gray-500">
                      <Clock className="h-4 w-4 mr-1" />
                      <span>{service?.duration_minutes} min</span>
                    </div>
                    <div className="flex items-center text-pink-600 font-semibold">
                      <DollarSign className="h-4 w-4" />
                      <span>
                        {typeof service?.price === "number"
                          ? `${service.price}`
                          : service?.price}
                      </span>
                    </div>
                  </div>
                  <button className="w-full mt-4 px-4 py-2 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all">
                    Reservar Ahora
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Detalle del servicio + horarios */
          <div className="max-w-4xl mx-auto">
            <button
              onClick={() => {
                setSelectedService(null);
                setSelectedSchedule(null);
              }}
              className="mb-6 text-pink-600 hover:text-pink-700 font-semibold flex items-center"
            >
              ← Volver a Servicios
            </button>

            <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
              <div className="flex items-start justify-between gap-6 mb-6">
                <div className="flex-1">
                  <h2 className="text-3xl font-bold text-gray-900 mb-2">
                    {selectedService.name}
                  </h2>
                  <p className="text-gray-600">{selectedService.description}</p>
                </div>

                {/* Miniatura en el detalle con fallback a emoji */}
                <div className="w-40 h-28 relative rounded-xl overflow-hidden bg-gray-50 shrink-0 flex items-center justify-center">
                  {getServiceImage(selectedService) ? (
                    <img
                      src={getServiceImage(selectedService)}
                      alt={selectedService.name}
                      loading="lazy"
                      className="absolute inset-0 w-full h-full object-cover"
                    />
                  ) : (
                    <div className="text-5xl">
                      {selectedService?.type === "coaching" ? "🎯" : "💆‍♀️"}
                    </div>
                  )}
                </div>

                <div className="text-right">
                  <div className="text-3xl font-bold text-pink-600">
                    {typeof selectedService.price === "number"
                      ? `$${selectedService.price}`
                      : selectedService.price}
                  </div>
                  <div className="text-sm text-gray-500">
                    {selectedService.duration_minutes} minutos
                  </div>
                </div>
              </div>
            </div>

            {/* Calendario / horarios disponibles */}
            {!selectedSchedule ? (
              <div className="bg-white rounded-2xl shadow-lg p-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                  <Calendar className="h-6 w-6 mr-2 text-pink-600" />
                  Horarios Disponibles
                </h3>

                {schedules.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">
                    No hay horarios disponibles en este momento. Por favor,
                    revisa más tarde.
                  </p>
                ) : (
                  <div className="space-y-4">
                    {groupByDate(schedules).map((group) => (
                      <div
                        key={group.date}
                        className="border border-gray-200 rounded-xl p-4"
                      >
                        <h4 className="font-semibold text-gray-900 mb-3">
                          {formatDate(group.date)}
                        </h4>
                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                          {group.slots.map((schedule) => (
                            <button
                              key={schedule.id}
                              onClick={() => setSelectedSchedule(schedule)}
                              className="px-4 py-3 border-2 border-pink-200 rounded-lg hover:border-pink-500 hover:bg-pink-50 transition-all font-medium text-gray-700 hover:text-pink-600"
                            >
                              {formatTime(schedule.start_time)}
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              /* Formulario de reserva */
              <div className="bg-white rounded-2xl shadow-lg p-8">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-2xl font-bold text-gray-900">
                    Completa tu Reserva
                  </h3>
                  <button
                    onClick={() => setSelectedSchedule(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="h-6 w-6" />
                  </button>
                </div>

                <div className="bg-pink-50 border border-pink-200 rounded-lg p-4 mb-6">
                  <p className="text-sm text-gray-600 mb-1">
                    Hora Seleccionada:
                  </p>
                  <p className="text-lg font-semibold text-gray-900">
                    {formatDate(selectedSchedule.date)} a las{" "}
                    {formatTime(selectedSchedule.start_time)}
                  </p>
                </div>

                {showSuccess ? (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
                    <Check className="h-12 w-12 text-green-600 mx-auto mb-3" />
                    <h4 className="text-xl font-bold text-green-900 mb-2">
                      ¡Reserva Confirmada!
                    </h4>
                    <p className="text-green-700">
                      Te enviaremos un correo electrónico de confirmación en
                      breve.
                    </p>
                  </div>
                ) : (
                  <form onSubmit={handleBooking} className="space-y-4">
                    {error && (
                      <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 text-sm">
                        {error}
                      </div>
                    )}

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Nombre Completo *
                      </label>
                      <input
                        type="text"
                        required
                        value={bookingForm.customer_name}
                        onChange={(e) =>
                          setBookingForm({
                            ...bookingForm,
                            customer_name: e.target.value,
                          })
                        }
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition-all"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Correo Electrónico *
                      </label>
                      <input
                        type="email"
                        required
                        value={bookingForm.customer_email}
                        onChange={(e) =>
                          setBookingForm({
                            ...bookingForm,
                            customer_email: e.target.value,
                          })
                        }
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition-all"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Teléfono *
                      </label>
                      <input
                        type="tel"
                        value={bookingForm.customer_phone}
                        onChange={(e) =>
                          setBookingForm({
                            ...bookingForm,
                            customer_phone: e.target.value,
                          })
                        }
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition-all"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Solicitudes Especiales o Notas
                      </label>
                      <textarea
                        rows={4}
                        value={bookingForm.notes}
                        onChange={(e) =>
                          setBookingForm({
                            ...bookingForm,
                            notes: e.target.value,
                          })
                        }
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition-all resize-none"
                      />
                    </div>

                    <button
                      type="submit"
                      className="w-full px-6 py-4 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all"
                    >
                      Confirmar Reserva
                    </button>
                  </form>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* helpers */
function groupByDate(list = []) {
  if (!Array.isArray(list)) return [];
  const acc = {};
  for (const s of list) {
    if (!acc[s.date]) acc[s.date] = [];
    acc[s.date].push(s);
  }
  return Object.keys(acc)
    .sort()
    .map((date) => ({ date, slots: acc[date] }));
}
