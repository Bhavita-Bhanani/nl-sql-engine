import axios from "axios";

// In production, set VITE_API_URL to your Railway backend URL
// e.g. https://your-app.up.railway.app
// In development, Vite proxy handles /api → localhost:8000
const baseURL = import.meta.env.VITE_API_URL || "/api";

const api = axios.create({ baseURL });

export default api;
