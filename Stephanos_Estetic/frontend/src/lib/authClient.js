// src/lib/authClient.js
export async function ensureCsrf() {
  await fetch("http://localhost:8000/api/auth/csrf/", { credentials: "include" });
}

export async function getCurrentUser() {
  const res = await fetch("http://localhost:8000/api/user/me/", {
    credentials: "include",
  });
  if (res.status === 401) return null;
  return res.json();
}

export async function logout() {
  // asegúrate de tener la cookie csrftoken
  await ensureCsrf();
  const csrf = document.cookie.split("; ").find(c => c.startsWith("csrftoken="))?.split("=")[1] || "";
  await fetch("http://localhost:8000/api/auth/logout/", {
    method: "POST",
    credentials: "include",
    headers: { "X-CSRFToken": csrf },
  });
}
