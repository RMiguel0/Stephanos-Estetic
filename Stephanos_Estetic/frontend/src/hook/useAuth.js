// src/hooks/useAuth.js
import { useEffect, useState } from "react";
import { ensureCsrf, getCurrentUser, logout } from "./lib/authClient";

export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        await ensureCsrf();
        const u = await getCurrentUser();
        setUser(u);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return {
    user,
    loading,
    loginWithGoogle: () => { window.location.href = "http://localhost:8000/accounts/google/login/"; },
    logout: async () => { await logout(); setUser(null); },
  };
}
