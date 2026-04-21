import axios from "axios";

const DEFAULT_BASE_URL = "http://127.0.0.1:8000";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? DEFAULT_BASE_URL,
  timeout: 10000,
});
