import { useRef, useState } from "react";
import { Upload, Image as ImageIcon, Shirt, CupSoda, Smartphone } from "lucide-react";
import { useSearchParams } from "react-router-dom";

const PRODUCTS = [
  { id: "tshirt", label: "T-Shirt", icon: Shirt, options: { sizes: ["S", "M", "L", "XL"], colors: ["white", "black", "pink"] } },
  { id: "mug", label: "Mug", icon: CupSoda, options: { colors: ["white", "black", "pink"] } },
  { id: "case", label: "Phone Case", icon: Smartphone, options: { models: ["iPhone 13", "iPhone 14", "Galaxy S23"] } },
];

export default function Personalization() {
  const [params] = useSearchParams();
  const productIdFromList = params.get("productId"); // si venías desde Products
  const [selected, setSelected] = useState(productIdFromList ? "case" : "tshirt"); // default
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [notes, setNotes] = useState("");
  const [options, setOptions] = useState({ size: "M", color: "white", model: "iPhone 14" });
  const [submitting, setSubmitting] = useState(false);
  const inputRef = useRef(null);

  const onPick = () => inputRef.current?.click();

  const onDrop = (e) => {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f) handleFile(f);
  };

  const onFileChange = (e) => {
    const f = e.target.files?.[0];
    if (f) handleFile(f);
  };

  const handleFile = (f) => {
    setFile(f);
    const url = URL.createObjectURL(f);
    setPreview(url);
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!file) return alert("Sube una imagen primero.");
    setSubmitting(true);
    try {
      // cuando tengas backend:
      // const form = new FormData();
      // form.append("image", file);
      // form.append("product_type", selected);
      // form.append("options", JSON.stringify(options));
      // form.append("notes", notes);
      // const res = await fetch("/api/personalizations/", { method: "POST", body: form });
      // if (!res.ok) throw new Error("Upload failed");

      // demo
      await new Promise((r) => setTimeout(r, 800));
      alert("¡Solicitud enviada! Te contactaremos para confirmar el pedido.");
      setFile(null);
      setPreview("");
      setNotes("");
    } catch (err) {
      alert("Ocurrió un error. Intenta nuevamente.");
    } finally {
      setSubmitting(false);
    }
  };

  const current = PRODUCTS.find((p) => p.id === selected);

  return (
    <section className="min-h-screen bg-gradient-to-b from-white to-pink-50 py-12">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <header className="text-center mb-10">
          <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            Personalización
          </h1>
          <p className="text-gray-600">
            Sube tu imagen, elige el producto y deja instrucciones. Nosotros nos encargamos del resto ✨
          </p>
        </header>

        {/* Selector de producto */}
        <div className="grid sm:grid-cols-1 gap-4 mb-8">
          {PRODUCTS.map((p) => {
            const Icon = p.icon;
            const active = selected === p.id;
            return (
              <button
                key={p.id}
                onClick={() => setSelected(p.id)}
                className={`flex items-center gap-3 p-4 rounded-xl border transition
                  ${active ? "border-pink-400 bg-pink-50" : "border-gray-200 hover:border-pink-300 hover:bg-pink-50"}`}
              >
                <Icon className={`h-5 w-5 ${active ? "text-pink-600" : "text-gray-500"}`} />
                <span className={`font-semibold ${active ? "text-pink-700" : "text-gray-800"}`}>{p.label}</span>
              </button>
            );
          })}
        </div>

        <form onSubmit={onSubmit} className="grid lg:grid-cols-2 gap-8">
          {/* Uploader */}
          <div
            onDrop={onDrop}
            onDragOver={(e) => e.preventDefault()}
            className="rounded-2xl border-2 border-dashed border-pink-200 bg-white p-6 flex flex-col items-center justify-center text-center"
          >
            {preview ? (
              <img src={preview} alt="preview" className="max-h-80 rounded-xl object-contain" />
            ) : (
              <>
                <div className="h-20 w-20 rounded-full bg-pink-50 flex items-center justify-center mb-4">
                  <ImageIcon className="h-10 w-10 text-pink-500" />
                </div>
                <p className="text-gray-700 font-medium">Arrastra tu imagen aquí</p>
                <p className="text-gray-500 text-sm">o</p>
                <button
                  type="button"
                  onClick={onPick}
                  className="mt-3 px-4 py-2 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all text-sm"
                >
                  Seleccionar archivo
                </button>
                <input
                  ref={inputRef}
                  type="file"
                  accept="image/*"
                  onChange={onFileChange}
                  className="hidden"
                />
                <p className="text-xs text-gray-500 mt-2">PNG, JPG (máx 10MB)</p>
              </>
            )}
          </div>

          {/* Opciones */}
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Opciones</h3>

            {/* Campos condicionales según producto */}
            {selected === "tshirt" && (
              <div className="grid sm:grid-cols-2 gap-4">
                <label className="space-y-1">
                  <span className="text-sm text-gray-600">Talla</span>
                  <select
                    value={options.size}
                    onChange={(e) => setOptions({ ...options, size: e.target.value })}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-pink-500 outline-none"
                  >
                    {PRODUCTS[0].options.sizes.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </label>
                <label className="space-y-1">
                  <span className="text-sm text-gray-600">Color</span>
                  <select
                    value={options.color}
                    onChange={(e) => setOptions({ ...options, color: e.target.value })}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-pink-500 outline-none"
                  >
                    {PRODUCTS[0].options.colors.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </label>
              </div>
            )}

            {selected === "mug" && (
              <label className="block space-y-1">
                <span className="text-sm text-gray-600">Color</span>
                <select
                  value={options.color}
                  onChange={(e) => setOptions({ ...options, color: e.target.value })}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-pink-500 outline-none"
                >
                  {PRODUCTS[1].options.colors.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </label>
            )}

            {selected === "case" && (
              <label className="block space-y-1">
                <span className="text-sm text-gray-600">Modelo</span>
                <select
                  value={options.model}
                  onChange={(e) => setOptions({ ...options, model: e.target.value })}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-pink-500 outline-none"
                >
                  {PRODUCTS[2].options.models.map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </label>
            )}

            {/* Notas */}
            <label className="block mt-4 space-y-1">
              <span className="text-sm text-gray-600">Notas / Instrucciones</span>
              <textarea
                rows="4"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-pink-500 outline-none resize-none"
                placeholder="Ej: imprimir al centro, 12cm, fondo transparente"
              />
            </label>

            <button
              type="submit"
              disabled={submitting}
              className="mt-6 w-full px-6 py-3 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-60"
            >
              {submitting ? "Enviando..." : "Enviar solicitud"}
            </button>
          </div>
        </form>
      </div>
    </section>
  );
}
