import axios from "axios";

const base =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

const api = axios.create({
  baseURL: base,
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("smartbus_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export default api;