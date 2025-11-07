// frontend/src/pages/BookingSuccess.jsx
import { useSearchParams } from "react-router-dom";

export default function BookingSuccess() {
  const [sp] = useSearchParams();
  const ok = sp.get("ok") === "true";
  const service = sp.get("service");
  const startsAt = sp.get("starts_at");
  const amount = sp.get("amount");

  if (!ok) {
    return <div className="max-w-3xl mx-auto p-8">Pago cancelado o rechazado.</div>;
  }

  return (
    <div className="max-w-3xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-4">¡Reserva confirmada!</h1>
      <p className="mb-2"><b>Servicio:</b> {service}</p>
      <p className="mb-2"><b>Fecha/Hora:</b> {startsAt}</p>
      <p className="mb-2"><b>Abono pagado:</b> ${amount} CLP</p>
      <p className="text-gray-600 mt-4">Te enviamos un correo con los detalles y un .ics para tu calendario.</p>
    </div>
  );
}
