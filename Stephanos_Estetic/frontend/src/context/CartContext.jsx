import { createContext, useContext, useEffect, useMemo, useState } from "react";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [items, setItems] = useState(() => {
    try {
      const raw = localStorage.getItem("cart_v1");
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    localStorage.setItem("cart_v1", JSON.stringify(items));
  }, [items]);

  const addItem = (product, qty = 1) => {
    setItems(prev => {
      const i = prev.findIndex(x => x.id === product.id);
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
    setItems(prev =>
      prev
        .map(x => (x.id === id ? { ...x, qty: Math.max(1, qty) } : x))
        .filter(x => x.qty > 0)
    );
  };

  const removeItem = (id) => setItems(prev => prev.filter(x => x.id !== id));
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
