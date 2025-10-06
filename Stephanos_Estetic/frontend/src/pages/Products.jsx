import { useState, useEffect } from "react";
import { Shirt, Sparkles, Package, Filter } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";

export default function Products() {
  const { addItem } = useCart();
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const categories = [
    { id: "all", label: "All Products", icon: Package },
    { id: "clothing", label: "Clothing", icon: Shirt },
    { id: "beauty", label: "Beauty Products", icon: Sparkles },
    { id: "personalization", label: "Personalization", icon: Filter },
  ];

  useEffect(() => {
    fetchProducts();
  }, []);

  useEffect(() => {
    if (selectedCategory === "all") {
      setFilteredProducts(products);
    } else {
      setFilteredProducts(products.filter((p) => p.category === selectedCategory));
    }
  }, [selectedCategory, products]);

  const fetchJSON = async (url) => {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  };

  const addToCart = (product) => {
    addItem(product, 1);
    setAddMsg("Añadido al carrito ✨");
    setTimeout(() => setAddMsg(""), 1500);
  };

  const fetchProducts = async () => {
    setLoading(true);
    try {
      // intenta tu backend (ajusta la URL si corresponde)
      const data = await fetchJSON("/api/products/");
      setProducts(data || []);
      setFilteredProducts(data || []);
    } catch (err) {
      console.warn("GET /api/products fallback:", err?.message);
      // fallback de demo para que la vista funcione
      const demo = [
        { id: "p1", name: "Hidratante Facial", price: 12990, category: "beauty", description: "Hidratación intensa.", featured: true },
        { id: "p2", name: "Protector Solar SPF50", price: 11990, category: "beauty", description: "Protección UVA/UVB." },
        { id: "p3", name: "Polera Básica", price: 8990, category: "clothing", description: "100% algodón, varios colores." },
        { id: "p4", name: "Taza Personalizable", price: 6990, category: "personalization", description: "Sube tu imagen y personaliza." },
        { id: "p5", name: "Carcasa Personalizable", price: 10990, category: "personalization", description: "iPhone / Samsung." },
      ];
      setProducts(demo);
      setFilteredProducts(demo);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryEmoji = (cat) => {
    switch (cat) {
      case "clothing":
        return "👗";
      case "beauty":
        return "💄";
      case "personalization":
        return "✨";
      default:
        return "📦";
    }
  };

  const handleView = (product) => {
    if (product.category === "personalization") {
      // Enlaza a la nueva vista de Personalización, opcional enviar id por query
      navigate(`/personalization?productId=${encodeURIComponent(product.id)}`);
    } else {
      // Aquí puedes navegar a un detalle futuro si quieres
      // navigate(`/products/${product.id}`)
      // Por ahora, nada:
    }
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
              Productos
            </span>
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Descubre nuestra selección curada de productos de belleza premium, ropa y artículos personalizados.
          </p>
        </div>

        {/* Filtros (mantenido) */}
        <div className="mb-10">
          <div className="flex flex-wrap justify-center gap-3">
            {categories.map((category) => {
              const Icon = category.icon;
              return (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold transition-all ${
                    selectedCategory === category.id
                      ? "bg-gradient-to-r from-pink-500 to-pink-600 text-white shadow-lg scale-105"
                      : "bg-white text-gray-700 border-2 border-gray-200 hover:border-pink-300 hover:bg-pink-50"
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{category.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Grid */}
        {filteredProducts.length === 0 ? (
          <div className="text-center py-16">
            <Package className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No se encontraron productos en esta categoría.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredProducts.map((product) => (
              <div
                key={product.id}
                className="bg-white rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100 hover:-translate-y-1 group"
              >
                <div className="relative h-64 bg-gradient-to-br from-pink-50 to-pink-100 flex items-center justify-center overflow-hidden">
                  <div className="text-7xl transform group-hover:scale-110 transition-transform duration-300">
                    {getCategoryEmoji(product.category)}
                  </div>
                  {product.featured && (
                    <div className="absolute top-3 right-3 bg-pink-600 text-white text-xs font-bold px-3 py-1 rounded-full">
                      Featured
                    </div>
                  )}
                </div>

                <div className="p-5">
                  <div className="inline-block px-3 py-1 bg-pink-100 text-pink-600 rounded-full text-xs font-semibold mb-3 uppercase">
                    {product.category}
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-1">
                    {product.name}
                  </h3>
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2 min-h-[2.5rem]">
                    {product.description}
                  </p>

                  <div className="flex items-center justify-between">
                    <div className="text-2xl font-bold text-pink-600">
                      {formatPrice(product.price)}
                    </div>

                    {product.category === "personalization" ? (
                      <button
                        onClick={() => handleView(product)}
                        className="px-4 py-2 bg-white text-pink-600 rounded-lg font-semibold border-2 border-pink-200 hover:border-pink-300 hover:bg-pink-50 transition-all text-sm"
                      >
                        Personalizar
                      </button>
                    ) : (
                      <button
                        onClick={() => addItem(product, 1)}
                        className="px-4 py-2 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg font-semibold hover:shadow-lg hover:scale-105 transition-all text-sm"
                      >
                        Añadir al carrito
                      </button>
                    )} 
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* CTA de Personalización */}
        <div className="mt-16 bg-white rounded-2xl shadow-lg p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-3">
            ¿Quieres algo único?
          </h2>
          <p className="text-gray-600 mb-6">
            Sube tu imagen y personaliza tazas, poleras, carcasas y más.
          </p>
          <Link
            to="/personalization"
            className="px-8 py-3 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all"
          >
            Ir a Personalización
          </Link>
        </div>
      </div>
    </div>
  );
}

/* helpers */
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
