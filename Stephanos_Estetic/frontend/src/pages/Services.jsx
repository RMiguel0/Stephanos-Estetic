export default function Services() {
  const servicios = [
    { name: "Limpieza facial", dur: "60 min", price: "$24.990" },
    { name: "Peeling químico", dur: "45 min", price: "$34.990" },
    { name: "Dermaplaning", dur: "45 min", price: "$29.990" },
    { name: "Masoterapia descontracturante", dur: "50 min", price: "$22.990" },
  ];
  return (
    <section className="site-container">
      <h1 className="text-3xl font-bold">Servicios</h1>
      <p className="text-gray-600 mt-2">Agenda tu tratamiento ideal.</p>

      <div className="mt-6 grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {servicios.map((s) => (
          <div key={s.name} className="card p-6">
            <h3 className="font-semibold">{s.name}</h3>
            <p className="text-gray-600 text-sm mt-1">{s.dur}</p>
            <div className="mt-4 flex items-center justify-between">
              <span className="font-semibold">{s.price}</span>
              <button className="btn-primary text-sm px-3 py-1.5">Reservar</button>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
