import { AlertCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";

const API_BASE =
  window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "http://localhost:8000";

export default function Login() {
  const navigate = useNavigate();

  const handleGoogleLogin = () => {
    // Redirige al flujo de OAuth de Google en allauth
    window.location.href = `${API_BASE}/accounts/google/login/`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-pink-50 py-12">
      <div className="max-w-md mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Bienvenido de nuevo
          </h1>
          <p className="text-gray-600">
            Inicia sesión usando tu cuenta de Google
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
          {/* Mensaje de error opcional */}
          {false && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
              <AlertCircle className="h-5 w-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
              <p className="text-red-700 text-sm">
                Ocurrió un error, intenta nuevamente.
              </p>
            </div>
          )}

          {/* Botón Google */}
          <div className="flex justify-center">
            <button
              onClick={handleGoogleLogin}
              className="w-full py-3 border border-gray-300 rounded-lg flex items-center justify-center hover:bg-gray-50 transition-all"
            >
              <img
                src="https://developers.google.com/identity/images/g-logo.png"
                alt="Google"
                className="w-5 h-5 mr-2"
              />
              Iniciar sesión con Google
            </button>
          </div>

          {/* Link opcional a registro, por si mantienes la vista de register */}
          <p className="text-center text-sm text-gray-600 mt-6">
            ¿No tienes una cuenta?{" "}
            <a
              href="/register"
              className="text-pink-600 hover:underline font-medium"
            >
              Regístrate
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
