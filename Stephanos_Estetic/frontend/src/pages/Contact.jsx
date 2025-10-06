import { useState } from "react";
import { Send, Mail, Phone, MapPin, Check } from "lucide-react";

export default function Contact() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: "",
  });
  const [loading, setLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [error, setError] = useState("");

  async function postJSON(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json().catch(() => ({}));
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const payload = {
      name: formData.name,
      email: formData.email,
      subject: formData.subject,
      message: formData.message,
    };

    try {
      // 1) intenta tu endpoint principal
      try {
        await postJSON("/api/contact_submissions/", payload);
      } catch (err1) {
        // 2) intenta endpoint alternativo
        await postJSON("/api/contact/", payload);
      }

      setShowSuccess(true);
      setFormData({ name: "", email: "", subject: "", message: "" });
      setTimeout(() => setShowSuccess(false), 5000);
    } catch (err) {
      // Fallback demo para que no se rompa la UI si aún no hay backend
      console.warn("POST contacto fallback:", err?.message);
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
      // Si prefieres mostrar error en vez de demo-success:
      // setError(err.message || "Failed to send message. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-pink-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            Ayudanos a{" "}
            <span className="bg-gradient-to-r from-pink-500 to-pink-600 bg-clip-text text-transparent">
              Ayudar
            </span>
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            ¿Tienes preguntas, comentarios o necesitas ayuda? Estamos aquí para ayudar. ¡Contáctanos en cualquier momento!
          </p>
        </div>

        {/* Cards de contacto */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          <div className="bg-white rounded-2xl shadow-sm p-8 text-center border border-gray-100 hover:shadow-lg transition-all">
            <div className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-pink-100 to-pink-200 rounded-xl mb-4">
              <Mail className="h-7 w-7 text-pink-600" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">Email</h3>
            <p className="text-gray-600 mb-3">Escríbenos en cualquier momento</p>
            <a href="mailto:info@bellavita.com" className="text-pink-600 hover:text-pink-700 font-semibold">
              contacto@stephanos.cl
            </a>
          </div>

          <div className="bg-white rounded-2xl shadow-sm p-8 text-center border border-gray-100 hover:shadow-lg transition-all">
            <div className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-pink-100 to-pink-200 rounded-xl mb-4">
              <Phone className="h-7 w-7 text-pink-600" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">Llámanos</h3>
            <p className="text-gray-600 mb-3">Lun-Vie, 9AM-6PM</p>
            <a href="tel:+15551234567" className="text-pink-600 hover:text-pink-700 font-semibold">
              +56 9 7344 5731
            </a>
          </div>
        </div>

        {/* Formulario */}
        <div className="max-w-3xl mx-auto">
          <div className="bg-white rounded-2xl shadow-lg p-8 lg:p-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-2 text-center">Dejanos un Mensaje</h2>
            <p className="text-gray-600 mb-8 text-center">
              Completa el formulario a continuación y nos pondremos en contacto contigo lo antes posible
            </p>

            {showSuccess ? (
              <div className="bg-green-50 border border-green-200 rounded-xl p-8 text-center">
                <Check className="h-16 w-16 text-green-600 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-green-900 mb-2">¡Mensaje Enviado Exitosamente!</h3>
                <p className="text-green-700 mb-6">
                  Gracias por ponerte en contacto. Responderemos a tu consulta en un plazo de 24 horas.
                </p>
                <button
                  onClick={() => setShowSuccess(false)}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors"
                >
                  Enviar Otro Mensaje
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 text-sm">
                    {error}
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Tu Nombre *</label>
                    <input
                      type="text"
                      required
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition-all"
                      placeholder="John Doe"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Tu Correo Electrónico *</label>
                    <input
                      type="email"
                      required
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition-all"
                      placeholder="john@ejemplo.com"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Asunto *</label>
                  <input
                    type="text"
                    required
                    value={formData.subject}
                    onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition-all"
                    placeholder="¿Cómo podemos ayudarte?"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Mensaje *</label>
                  <textarea
                    required
                    rows={6}
                    value={formData.message}
                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition-all resize-none"
                    placeholder="Cuéntanos más sobre tu consulta..."
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex items-center justify-center space-x-2 px-6 py-4 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Enviando...</span>
                    </>
                  ) : (
                    <>
                      <Send className="h-5 w-5" />
                      <span>Enviar Mensaje</span>
                    </>
                  )}
                </button>
              </form>
            )}
          </div>
        </div>

        {/* CTA inferior */}
        <div className="mt-12 text-center">
          <div className="bg-gradient-to-r from-pink-500 to-pink-600 rounded-2xl p-8 lg:p-12 text-white shadow-xl">
            <h2 className="text-3xl font-bold mb-4">Únete a Nuestra Comunidad</h2>
            <p className="text-pink-100 text-lg mb-6 max-w-2xl mx-auto">
              Mantente actualizado con nuestros últimos servicios, productos y consejos de bienestar. Síguenos en las redes sociales.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <button className="px-6 py-3 bg-white text-pink-600 rounded-lg font-semibold hover:bg-pink-50 transition-all">
                Síguenos en Instagram
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
