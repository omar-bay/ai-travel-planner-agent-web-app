import axios from "axios";
import { getToken, isTokenValid, clearToken } from "../utils/auth";

export const API = axios.create({
  baseURL: "http://localhost:8000/api",
  timeout: 30000,
});

API.interceptors.request.use((config) => {
  const token = getToken();
  if (token && isTokenValid(token)) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Optional: if 401, clear token so user is kicked back to login on next guard check
API.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err?.response?.status === 401) {
      clearToken();
    }
    return Promise.reject(err);
  }
);
