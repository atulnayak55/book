import axios from "axios";

function getDefaultBaseUrl(): string {
  if (typeof window === "undefined") {
    return "http://127.0.0.1:8000";
  }

  const { hostname, origin, port } = window.location;
  if (port === "5173" || port === "5174") {
    return `http://${hostname}:8000`;
  }

  return origin;
}

const DEFAULT_BASE_URL = getDefaultBaseUrl();

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? DEFAULT_BASE_URL,
  timeout: 10000,
});

export const backendBaseUrl = api.defaults.baseURL ?? DEFAULT_BASE_URL;
