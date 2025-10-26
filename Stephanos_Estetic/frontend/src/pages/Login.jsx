import { useState } from "react";
import { Mail, Lock, AlertCircle } from "lucide-react";
import { Link } from "react-router-dom";

/**
 * Login page component
 *
 * This React component implements a sign‑in form styled to match the rest of
 * the project. When the form is submitted it attempts to authenticate the
 * user against the Django backend via a POST request to `/accounts/login/`.
 * On successful login the optional `onNavigate` callback will be invoked
 * with `'profile'` so that the parent can switch to the profile page. Any
 * errors returned from the server are displayed to the user.
 */
export default function Login({ onNavigate }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ email: "", password: "" });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      // Attempt to authenticate against the Django backend.  The backend
      // should accept a JSON payload containing the user’s email and password.
      const response = await fetch("/accounts/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: form.email,
          password: form.password,
        }),
      });
      if (!response.ok) {
        // Try to extract a message from the response body for more detailed errors
        let msg = "Invalid credentials";
        try {
          const data = await response.json();
          if (data && data.detail) msg = data.detail;
        } catch (err) {
          // Ignore JSON parse errors – fall back to generic message
        }
        setError(msg);
      } else {
        // On success, navigate to the profile page
        if (onNavigate) onNavigate("profile");
      }
    } catch (err) {
      setError("Unable to sign in. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-pink-50 py-12">
      <div className="max-w-md mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Bienvenido de nuevo
          </h1>
          <p className="text-gray-600">
            Inicia sesión para acceder a tu cuenta
          </p>
        </div>
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
              <AlertCircle className="h-5 w-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Dirección de correo electrónico
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="email"
                  required
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition-all"
                  placeholder="you@example.com"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Contraseña
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="password"
                  required
                  value={form.password}
                  onChange={(e) =>
                    setForm({ ...form, password: e.target.value })
                  }
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition-all"
                  placeholder="••••••••"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Iniciando sesión...
                </div>
              ) : (
                "Iniciar sesión"
              )}
            </button>
          </form>
          <p className="text-center text-sm text-gray-600 mt-6">
            ¿No tienes una cuenta?{" "}
            <Link
              to="/register"
              className="text-pink-600 hover:underline font-medium"
            >
              Crea una
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
