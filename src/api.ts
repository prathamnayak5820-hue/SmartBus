import axios from "axios";

const base = import.meta.env.DEV
  ? ""
  : import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

const api = axios.create({
  baseURL: base.replace(/\/$/, ""),
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem("smartbus_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginRequest = String(error.config?.url || "").includes("/api/auth/login");
    if (error.response?.status === 401 && !isLoginRequest && sessionStorage.getItem("smartbus_token")) {
      window.dispatchEvent(new Event("smartbus:session-expired"));
    }
    return Promise.reject(error);
  }
);

export default api;