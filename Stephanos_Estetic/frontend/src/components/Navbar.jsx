import { NavLink, Link } from "react-router-dom";
import { Menu, X } from "lucide-react";
import { useState, useEffect } from "react";
import logo from "../assets/logo.svg";

const API_BASE = "http://localhost:8000"; // backend Django

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [isAuthenticated, setAuthenticated] = useState(false);

  // Comprueba sesión al montar
  useEffect(() => {
    fetch(`${API_BASE}/api/user/me/`, { credentials: "include" })
      .then((res) => res.json())
      .then((data) => {
        setAuthenticated(data?.is_authenticated ?? false);
      })
      .catch(() => setAuthenticated(false));
  }, []);

  const loginUrl = `${API_BASE}/accounts/google/login/`;
  const logoutUrl = `${API_BASE}/accounts/logout/?next=${encodeURIComponent(
    window.location.origin
  )}`;

  const linkBase =
    "px-3 py-2 rounded-md text-sm font-medium transition";
  const linkActive = "text-[var(--color-brand-600)] bg-[var(--color-brand-50)]";
  const linkInactive = "text-gray-700 hover:text-gray-900";

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur border-b border-gray-100">
      <nav className="site-container h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <img src={logo} alt="Stephanos Estetic" className="h-8 w-auto" />
          <span className="font-semibold tracking-tight">Stephanos Estetic</span>
        </Link>

        {/* desktop */}
        <div className="hidden md:flex items-center gap-1">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `${linkBase} ${isActive ? linkActive : linkInactive}`
            }
          >
            Inicio
          </NavLink>
          <NavLink
            to="/services"
            className={({ isActive }) =>
              `${linkBase} ${isActive ? linkActive : linkInactive}`
            }
          >
            Servicios
          </NavLink>
          <NavLink
            to="/products"
            className={({ isActive }) =>
              `${linkBase} ${isActive ? linkActive : linkInactive}`
            }
          >
            Productos
          </NavLink>
          <NavLink
            to="/contact"
            className={({ isActive }) =>
              `${linkBase} ${isActive ? linkActive : linkInactive}`
            }
          >
            Contacto
          </NavLink>
          <NavLink
            to="/cart"
            className={({ isActive }) =>
              `${linkBase} ${isActive ? linkActive : linkInactive}`
            }
          >
            🛒
          </NavLink>
          {isAuthenticated ? (
            <>
              <NavLink
                to="/profile"
                className={({ isActive }) =>
                  `${linkBase} ${isActive ? linkActive : linkInactive}`
                }
              >
                Mi perfil
              </NavLink>
              <a
                href={logoutUrl}
                className={`${linkBase} ${linkInactive}`}
              >
                Cerrar sesión
              </a>
            </>
          ) : (
            <a
              href={loginUrl}
              className={`${linkBase} ${linkInactive}`}
            >
              Iniciar sesión
            </a>
          )}
        </div>

        {/* mobile */}
        <button
          className="md:hidden p-2 rounded hover:bg-black/5"
          onClick={() => setOpen((v) => !v)}
          aria-label="Abrir menú"
        >
          {open ? <X /> : <Menu />}
        </button>
      </nav>

      {/* dropdown mobile */}
      {open && (
        <div className="md:hidden border-t border-gray-100 bg-white">
          <div className="site-container py-2 flex flex-col">
            {[
              { to: "/", label: "Inicio", end: true },
              { to: "/services", label: "Servicios" },
              { to: "/products", label: "Productos" },
              { to: "/contact", label: "Contacto" },
            ].map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.end}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  `py-2 ${isActive ? "font-semibold text-gray-900" : "text-gray-700"}`
                }
              >
                {l.label}
              </NavLink>
            ))}

            {isAuthenticated ? (
              <>
                <NavLink
                  to="/profile"
                  onClick={() => setOpen(false)}
                  className={({ isActive }) =>
                    `py-2 ${
                      isActive ? "font-semibold text-gray-900" : "text-gray-700"
                    }`
                  }
                >
                  Mi perfil
                </NavLink>
                <a
                  href={logoutUrl}
                  onClick={() => setOpen(false)}
                  className="py-2 text-gray-700"
                >
                  Cerrar sesión
                </a>
              </>
            ) : (
              <a
                href={loginUrl}
                onClick={() => setOpen(false)}
                className="py-2 text-gray-700"
              >
                Iniciar sesión
              </a>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
