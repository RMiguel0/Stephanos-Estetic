import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  User,
  Mail,
  Phone,
  Save,
  AlertCircle,
  CheckCircle,
} from "lucide-react";

// Utils: backend base y helpers
const API_BASE =
  window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "http://localhost:8000";

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
}

async function ensureCsrf() {
  await fetch(`${API_BASE}/api/auth/csrf/`, { credentials: "include" });
}

export default function UserProfile({ onNavigate }) {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [formData, setFormData] = useState({ full_name: "", phone: "" });

  const goToOrders = () => {
    if (onNavigate) {
      onNavigate("orders"); // si te pasan el prop, úsalo
    } else {
      navigate("/orders"); // si no, navega con react-router
    }
  };

  useEffect(() => {
    async function fetchAll() {
      setError("");
      try {
        await ensureCsrf();

        // 1) Chequea sesión por flag (no por status 401)
        const meRes = await fetch(`${API_BASE}/api/user/me/`, {
          credentials: "include",
        });
        const me = await meRes.json();

        if (!me?.is_authenticated) {
          // sin sesión -> manda directo al flujo de Google o a /login
          window.location.href = `${API_BASE.replace(
            /\/$/,
            ""
          )}/accounts/google/login/`;
          return;
        }

        // 2) Carga perfil si existe; si no, usa datos de /user/me/ SIN marcar error
        const profRes = await fetch(`${API_BASE}/api/profile/`, {
          credentials: "include",
        });

        if (profRes.ok) {
          const data = await profRes.json();

          const safe = {
            full_name:
              data.full_name ??
              (`${me.first_name || ""} ${me.last_name || ""}`.trim() ||
                me.username),
            email: data.email ?? me.email ?? "",
            phone: data.phone ?? "",
            picture: data.picture ?? "",
            created_at: data.created_at ?? "",
          };
          setProfile(safe);
          setFormData({
            full_name: safe.full_name || "",
            phone: safe.phone || "",
          });
          setError("");
        } else {
          // No hay endpoint /api/profile -> no lo consideres error
          const safe = {
            full_name:
              `${me.first_name || ""} ${me.last_name || ""}`.trim() ||
              me.username,
            email: me.email || "",
            phone: "",
            created_at: "",
          };
          setProfile(safe);
          setFormData({ full_name: safe.full_name || "", phone: "" });
        }
      } catch (err) {
        setError("No se pudo cargar el perfil.");
        setProfile({ full_name: "", email: "", phone: "", created_at: "" });
      } finally {
        setLoading(false);
      }
    }
    fetchAll();
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSuccess(false);

    try {
      // Asegura CSRF antes de un POST/PUT protegido
      await ensureCsrf();
      const csrf = getCookie("csrftoken") || "";

      const res = await fetch(`${API_BASE}/api/profile/`, {
        method: "PUT",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrf,
        },
        body: JSON.stringify({
          full_name: formData.full_name,
          phone: formData.phone,
        }),
      });

      if (!res.ok) {
        let msg = "Failed to update profile";
        try {
          const data = await res.json();
          if (data?.detail) msg = data.detail;
        } catch {}
        setError(msg);
      } else {
        setSuccess(true);
        setEditing(false);
        try {
          const updated = await res.json();
          setProfile((prev) => ({
            ...prev,
            ...updated,
            // asegura que email no se pierda si el backend no lo devuelve
            email: updated.email ?? prev?.email ?? "",
          }));
        } catch {
          // si el backend no retorna body, al menos refleja lo editado
          setProfile((prev) => ({
            ...prev,
            full_name: formData.full_name,
            phone: formData.phone,
          }));
        }
        setTimeout(() => setSuccess(false), 3000);
      }
    } catch (err) {
      setError("Unable to update profile. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600"></div>
      </div>
    );
  }

  if (!profile) return null;

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-pink-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Mi{" "}
            <span className="bg-gradient-to-r from-pink-500 to-pink-600 bg-clip-text text-transparent">
              Perfil
            </span>
          </h1>
          <p className="text-gray-600">
            {" "}
            Maneja tu información personal y preferencias.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-sm p-6 border border-gray-100 text-center">
              <div className="inline-flex items-center justify-center w-24 h-24 rounded-full mb-4 overflow-hidden bg-gradient-to-br from-pink-100 to-pink-200">
                {profile.picture ? (
                  <img
                    src={profile.picture}
                    alt={profile.full_name || "Foto de perfil"}
                    className="object-cover w-full h-full"
                    referrerPolicy="no-referrer" // evita bloqueos de imagen Google
                  />
                ) : (
                  <User className="h-12 w-12 text-pink-600" />
                )}
              </div>

              <h2 className="text-xl font-bold text-gray-900 mb-1">
                {profile.full_name || "Usuario"}
              </h2>
              <p className="text-sm text-gray-600 mb-6">{profile.email}</p>

              <div className="space-y-2">
                <button
                  onClick={goToOrders}
                  className="w-full px-4 py-2 bg-pink-50 text-pink-600 rounded-lg font-semibold hover:bg-pink-100 transition-all"
                >
                  Ver mis pedidos
                </button>
              </div>
            </div>
          </div>

          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-sm p-8 border border-gray-100">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-gray-900">
                  Información Personal
                </h3>
                {!editing && (
                  <button
                    onClick={() => setEditing(true)}
                    className="px-4 py-2 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all"
                  >
                    Editar perfil
                  </button>
                )}
              </div>

              {success && (
                <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                  <p className="text-green-700 text-sm">
                    ¡Perfil actualizado con éxito!
                  </p>
                </div>
              )}

              {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
                  <AlertCircle className="h-5 w-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              )}

              {editing ? (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nombre completo
                    </label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                      <input
                        type="text"
                        value={formData.full_name}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            full_name: e.target.value,
                          })
                        }
                        className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition-all"
                        placeholder="Tu nombre completo"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Dirección de correo electrónico
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                      <input
                        type="email"
                        value={profile.email}
                        disabled
                        className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 cursor-not-allowed"
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Correo electrónico no se puede cambiar
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Número de teléfono
                    </label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                      <input
                        type="tel"
                        value={formData.phone}
                        onChange={(e) =>
                          setFormData({ ...formData, phone: e.target.value })
                        }
                        className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition-all"
                        placeholder="Tu número de teléfono"
                      />
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <button
                      type="submit"
                      disabled={saving}
                      className="flex-1 px-6 py-3 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                    >
                      {saving ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                          Guardando...
                        </>
                      ) : (
                        <>
                          <Save className="h-5 w-5 mr-2" />
                          Guardar cambios
                        </>
                      )}
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setEditing(false);
                        setFormData({
                          full_name: profile.full_name || "",
                          phone: profile.phone || "",
                        });
                        setError("");
                      }}
                      className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition-all"
                    >
                      Cancelar
                    </button>
                  </div>
                </form>
              ) : (
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">
                      Nombre completo
                    </label>
                    <p className="text-lg text-gray-900">
                      {profile.full_name || "No proporcionado"}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">
                      Dirección de correo electrónico
                    </label>
                    <p className="text-lg text-gray-900">{profile.email}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">
                      Número de teléfono
                    </label>
                    <p className="text-lg text-gray-900">
                      {profile.phone || "No proporcionado"}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">
                      Miembro desde
                    </label>
                    <p className="text-lg text-gray-900">
                      {profile.created_at
                        ? new Date(profile.created_at).toLocaleDateString(
                            "es-CL",
                            {
                              year: "numeric",
                              month: "long",
                              day: "numeric",
                            }
                          )
                        : "—"}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
