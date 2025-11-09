// Tiny cookie helpers (no deps)
export function setCookie(name, value, opts = {}) {
  const { expires, path = "/", secure = false } = opts;
  let cookie = `${encodeURIComponent(name)}=${encodeURIComponent(value)}; path=${path}`;
  if (expires instanceof Date) cookie += `; expires=${expires.toUTCString()}`;
  if (secure) cookie += `; Secure`;
  // SameSite=Lax so redirects still send cookie, adjust if you run cross-site
  cookie += `; SameSite=Lax`;
  document.cookie = cookie;
}

export function getCookie(name) {
  return document.cookie
    .split("; ")
    .map((c) => c.split("="))
    .reduce((acc, [k, v]) => ({ ...acc, [decodeURIComponent(k)]: decodeURIComponent(v || "") }), {})[name];
}

export function deleteCookie(name) {
  document.cookie = `${encodeURIComponent(name)}=; Max-Age=0; path=/; SameSite=Lax`;
}

// JWT helpers
export function decodeJwt(token) {
  try {
    const [, payload] = token.split(".");
    return JSON.parse(atob(payload));
  } catch {
    return null;
  }
}

export function getToken() {
  return getCookie("access_token") || null;
}

export function setToken(token) {
  const payload = decodeJwt(token);
  // Honor exp if present
  if (payload?.exp) {
    const expDate = new Date(payload.exp * 1000);
    setCookie("access_token", token, { expires: expDate, path: "/" });
  } else {
    // fallback: session cookie
    setCookie("access_token", token, { path: "/" });
  }
}

export function clearToken() {
  deleteCookie("access_token");
}

export function isTokenValid(token = getToken()) {
  if (!token) return false;
  const payload = decodeJwt(token);
  if (!payload?.exp) return true; // if no exp, treat as valid (or flip to false if you prefer)
  const now = Math.floor(Date.now() / 1000);
  return payload.exp > now;
}
