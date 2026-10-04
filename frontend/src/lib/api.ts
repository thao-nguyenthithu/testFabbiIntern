import axios, { type InternalAxiosRequestConfig } from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor: attach Bearer token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Shared by all requests that get 401 at the same time
let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) {
    throw new Error("No refresh token");
  }
  // Plain axios so this call does not go through the 401 interceptor
  const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
    refresh_token: refreshToken,
  });
  localStorage.setItem("access_token", response.data.access_token);
  localStorage.setItem("refresh_token", response.data.refresh_token);
  return response.data.access_token;
}

// Response interceptor: refresh the access token once on 401, then retry
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const request = error.config as
      | (InternalAxiosRequestConfig & { _retry?: boolean })
      | undefined;
    // A failed login also returns 401; let the login form show that error.
    const isLoginRequest = request?.url === "/auth/login";
    if (error.response?.status !== 401 || !request || isLoginRequest) {
      return Promise.reject(error);
    }

    if (!request._retry) {
      request._retry = true;
      try {
        refreshPromise ??= refreshAccessToken().finally(() => {
          refreshPromise = null;
        });
        const token = await refreshPromise;
        request.headers.Authorization = `Bearer ${token}`;
        return api(request);
      } catch {
        // Refresh failed: fall through and log out
      }
    }

    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/login";
    return Promise.reject(error);
  }
);
