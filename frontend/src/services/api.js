import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
  timeout: 8000,
  headers: {
    "Content-Type": "application/json"
  }
});

// Demo-only session: the logged-in demo user's email is sent on every request.
// The BACKEND looks the user up and enforces the role (401 / 403).
export const USER_STORAGE_KEY = "campusfind_user";

API.interceptors.request.use((config) => {
  try {
    const saved = JSON.parse(localStorage.getItem(USER_STORAGE_KEY) || "null");
    if (saved?.email) config.headers["X-User-Email"] = saved.email;
  } catch {
    /* ignore corrupted session */
  }
  return config;
});

// Auth (demo)
export const getDemoUsers = () => API.get("/auth/demo-users");
export const loginDemo = (email) => API.post("/auth/login", { email });

// Items API (public)
export const getItems = (params) => API.get("/items", { params });
export const getItem = (id) => API.get(`/items/${id}`);
export const createItem = (data) => API.post("/items", data);
export const getMyItems = () => API.get("/items/my");

// Claims API (student)
export const createClaim = (data) => API.post("/claims", data);
export const getMyClaims = () => API.get("/claims/my");

// Admin API
export const getAdminStats = () => API.get("/admin/stats");
export const getAdminClaims = (params) => API.get("/admin/claims", { params });
export const getAdminClaim = (id) => API.get(`/admin/claims/${id}`);
export const decideClaim = (id, data) => API.patch(`/admin/claims/${id}`, data);
export const updateHandover = (id, data) => API.patch(`/admin/claims/${id}/handover`, data);
export const markItemRecovered = (itemId) => API.patch(`/admin/items/${itemId}/recovered`);

// Upload API
export const uploadImage = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return API.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
};

export default API;
