import { NavLink, Link } from "react-router-dom";
import { Menu, X } from "lucide-react";
import { useState } from "react";
import logo from "../assets/logo.svg"; // ajusta si tu logo es .svg

export default function Navbar() {
  const [open, setOpen] = useState(false);

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
          <NavLink to="/" end className={({isActive}) => `${linkBase} ${isActive?linkActive:linkInactive}`}>Inicio</NavLink>
          <NavLink to="/services" className={({isActive}) => `${linkBase} ${isActive?linkActive:linkInactive}`}>Servicios</NavLink>
          <NavLink to="/products" className={({isActive}) => `${linkBase} ${isActive?linkActive:linkInactive}`}>Productos</NavLink>
          <NavLink to="/contact" className={({isActive}) => `${linkBase} ${isActive?linkActive:linkInactive}`}>Contacto</NavLink>
          <NavLink to="/cart" className={({isActive}) => `${linkBase} ${isActive?linkActive:linkInactive}`}>🛒</NavLink>
          <NavLink to="/login" className={({isActive}) => `${linkBase} ${isActive?linkActive:linkInactive}`}>Iniciar sesión</NavLink>
        </div>

        {/* mobile */}
        <button
          className="md:hidden p-2 rounded hover:bg-black/5"
          onClick={() => setOpen(v => !v)}
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
              {to:"/", label:"Inicio", end:true},
              {to:"/services", label:"Servicios"},
              {to:"/products", label:"Productos"},
              {to:"/contact", label:"Contacto"},
            ].map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.end}
                onClick={() => setOpen(false)}
                className={({isActive}) => `py-2 ${isActive ? "font-semibold text-gray-900" : "text-gray-700"}`}
              >
                {l.label}
              </NavLink>
            ))}
          </div>
        </div>
      )}
    </header>
  );
}
