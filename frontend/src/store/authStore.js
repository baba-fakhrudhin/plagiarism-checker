import { create } from "zustand";
import api from "../api/client";

export const useAuthStore = create((set, get) => ({
  user: null,
  token: localStorage.getItem("token") || null,
  isLoading: false,
  error: null,

  // ----------------------------
  // SIGNUP
  // ----------------------------
  signup: async (email, username, password) => {
    set({ isLoading: true, error: null });

    try {
      const res = await api.post("/auth/signup", {
        email,
        username,
        password,
      });

      const { access_token, user } = res.data;

      localStorage.setItem("token", access_token);

      set({
        user,
        token: access_token,
        isLoading: false,
      });

      return { success: true };
    } catch (err) {
      set({
        error: err.response?.data?.error || "Signup failed",
        isLoading: false,
      });

      return { success: false };
    }
  },

  // ----------------------------
  // LOGIN
  // ----------------------------
  login: async (email, password) => {
    set({ isLoading: true, error: null });

    try {
      const res = await api.post("/auth/login", {
        email,
        password,
      });

      const { access_token, user } = res.data;

      localStorage.setItem("token", access_token);

      set({
        user,
        token: access_token,
        isLoading: false,
      });

      return { success: true };
    } catch (err) {
      set({
        error: err.response?.data?.error || "Invalid credentials",
        isLoading: false,
      });

      return { success: false };
    }
  },

  // ----------------------------
  // LOGOUT
  // ----------------------------
  logout: () => {
    localStorage.removeItem("token");

    set({
      user: null,
      token: null,
      error: null,
    });
  },

  // ----------------------------
  // CHECK AUTH (On App Load)
  // ----------------------------
  checkAuth: async () => {
    const token = localStorage.getItem("token");

    if (!token) {
      set({ user: null, token: null });
      return;
    }

    try {
      const res = await api.get("/auth/me");

      set({
        user: res.data,
        token,
      });
    } catch (err) {
      localStorage.removeItem("token");

      set({
        user: null,
        token: null,
      });
    }
  },

  // ----------------------------
  // UPDATE PROFILE
  // ----------------------------
  updateProfile: async (data) => {
    set({ isLoading: true, error: null });

    try {
      const res = await api.put("/auth/me", data);

      set({
        user: res.data.user,
        isLoading: false,
      });

      return { success: true };
    } catch (err) {
      set({
        error: err.response?.data?.error || "Update failed",
        isLoading: false,
      });

      return { success: false };
    }
  },

  // ----------------------------
  // CLEAR ERROR
  // ----------------------------
  clearError: () => set({ error: null }),
}));
