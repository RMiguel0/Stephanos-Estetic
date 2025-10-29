import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

const CartContext = createContext(null);

// --- Helpers (mismo patrón que usas en UserProfile/Orders) ---
const API_BASE =
  window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "http://localhost:8000";

function storageKeyFor(user) {
  return user?.id ? `cart:${user.id}` : "cart:anon";
}

async function getCurrentUser() {
  try {
    const res = await fetch(`${API_BASE}/api/user/me/`, {
      credentials: "include",
    });
    return await res.json(); // { is_authenticated, id, ... }
  } catch {
    return { is_authenticated: false };
  }
}
// --------------------------------------------------------------

export function CartProvider({ children }) {
  const [user, setUser] = useState(null);
  const [items, setItems] = useState([]);
  const migratedRef = useRef(false); // evita migrar 2 veces

  // 1) Cargar usuario al montar
  useEffect(() => {
    let alive = true;
    (async () => {
      const me = await getCurrentUser();
      if (!alive) return;
      setUser(me?.is_authenticated ? me : null);
    })();
    return () => {
      alive = false;
    };
  }, []);

  // 2) Clave de storage por usuario
  const storageKey = useMemo(() => storageKeyFor(user), [user]);

  // 3) Cargar carrito cuando cambia la clave (anon <-> user)
  useEffect(() => {
    try {
      const raw = localStorage.getItem(storageKey);
      setItems(raw ? JSON.parse(raw) : []);
    } catch {
      setItems([]);
    }
  }, [storageKey]);

  // 4) Guardar carrito bajo la clave actual
  useEffect(() => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(items));
    } catch {}
  }, [storageKey, items]);

  // 5) Migrar cart:anon => cart:<user_id> al iniciar sesión (fusiona cantidades por id)
  // 5) Migrar cart:anon => cart:<user_id> al iniciar sesión (fusiona cantidades)
  useEffect(() => {
    // solo si hay usuario logueado y no migrado aún
    if (!user?.id || migratedRef.current) return;

    const anonRaw = localStorage.getItem("cart:anon");
    if (!anonRaw) {
      migratedRef.current = true;
      return;
    }

    try {
      const anonItems = JSON.parse(anonRaw) || [];
      if (!Array.isArray(anonItems) || anonItems.length === 0) {
        migratedRef.current = true;
        return;
      }

      // cargamos también el carrito actual del usuario (si existe)
      const userCartRaw = localStorage.getItem(storageKeyFor(user));
      const userCart = userCartRaw ? JSON.parse(userCartRaw) : [];

      // fusionar los dos arrays
      const map = new Map();
      [...anonItems, ...userCart].forEach((it) => {
        const key = it.id;
        const old = map.get(key);
        map.set(key, old ? { ...it, qty: (old.qty || 0) + (it.qty || 0) } : it);
      });
      const merged = Array.from(map.values());

      // guardar en la nueva clave y actualizar estado
      localStorage.setItem(storageKeyFor(user), JSON.stringify(merged));
      localStorage.removeItem("cart:anon");
      setItems(merged);

      migratedRef.current = true;
    } catch (err) {
      console.error("Error migrando carrito:", err);
      migratedRef.current = true;
    }
  }, [user?.id]);

  // --- Acciones del carrito (las tuyas, sin cambios de API) ---
  const addItem = (product, qty = 1) => {
    setItems((prev) => {
      const i = prev.findIndex((x) => x.id === product.id);
      if (i >= 0) {
        const next = [...prev];
        next[i] = { ...next[i], qty: next[i].qty + qty };
        return next;
      }
      return [
        ...prev,
        {
          id: product.id,
          name: product.name,
          price: product.price || 0,
          image_url: product.image_url || "",
          qty,
          category: product.category || "",
        },
      ];
    });
  };

  const updateQty = (id, qty) => {
    setItems((prev) =>
      prev
        .map((x) => (x.id === id ? { ...x, qty: Math.max(1, qty) } : x))
        .filter((x) => x.qty > 0)
    );
  };

  const removeItem = (id) =>
    setItems((prev) => prev.filter((x) => x.id !== id));
  const clearCart = () => setItems([]);

  const subtotal = useMemo(
    () => items.reduce((acc, it) => acc + (it.price || 0) * (it.qty || 0), 0),
    [items]
  );

  const value = { items, addItem, updateQty, removeItem, clearCart, subtotal };
  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within CartProvider");
  return ctx;
}
