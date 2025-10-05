export default function Products() {
  const productos = [
    { name: "Hidratante facial", price: "$12.990" },
    { name: "Protector solar SPF50", price: "$11.990" },
    { name: "Sérum vitamina C", price: "$16.990" },
  ];
  return (
    <section className="site-container">
      <h1 className="text-3xl font-bold">Productos</h1>
      <p className="text-gray-600 mt-2">Recomendados por nuestros especialistas.</p>

      <div className="mt-6 grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {productos.map((p) => (
          <div key={p.name} className="card p-6">
            <div className="aspect-video rounded-lg bg-gray-50" />
            <h3 className="font-semibold mt-3">{p.name}</h3>
            <div className="mt-2 font-semibold">{p.price}</div>
            <button className="mt-3 btn-ghost text-sm">Agregar</button>
          </div>
        ))}
      </div>
    </section>
  );
}
