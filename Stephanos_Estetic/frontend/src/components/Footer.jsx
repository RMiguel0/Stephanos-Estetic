export default function Footer() {
  return (
    <footer className="mt-12 border-t border-gray-100 bg-white">
      <div className="site-container py-8 grid gap-6 md:grid-cols-3 text-sm">
        <div>
          <h4 className="font-semibold mb-2">Stephanos Estetic</h4>
          <p className="text-gray-600">Cuidado estético y bienestar. Reserva tu hora con nosotros ✨</p>
        </div>
        <div>
          <h4 className="font-semibold mb-2">Contacto</h4>
          <ul className="text-gray-600 space-y-1">
            <li>+56 9 7344 5731</li>
            <li>contacto@stephanos.cl</li>
          </ul>
        </div>
        <div>
          <h4 className="font-semibold mb-2">Horarios</h4>
          <ul className="text-gray-600 space-y-1">
            <li>Lun–Vie: 10:00–19:00</li>
            <li>Sáb: 10:00–14:00</li>
          </ul>
        </div>
      </div>
      <div className="text-center py-4 text-xs text-gray-500">
        © {new Date().getFullYear()} Stephanos Estetic. Todos los derechos reservados.
      </div>
    </footer>
  );
}
