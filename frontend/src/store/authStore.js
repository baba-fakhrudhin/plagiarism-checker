import { create } from 'zustand';
import api from '../api/client';

export const useAuthStore = create((set, get) => ({
  user: null,
  token: localStorage.getItem('token'),
  isLoading: false,
  error: null,

  signup: async (email, username, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.post('/auth/signup', {
        email,
        username,
        password,
      });
      localStorage.setItem('token', response.data.access_token);
      set({
        user: response.data.user,
        token: response.data.access_token,
        isLoading: false,
      });
      return true;
    } catch (error) {
      set({
        error: error.response?.data?.error || 'Signup failed',
        isLoading: false,
      });
      return false;
    }
  },

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.post('/auth/login', { email, password });
      localStorage.setItem('token', response.data.access_token);
      set({
        user: response.data.user,
        token: response.data.access_token,
        isLoading: false,
      });
      return true;
    } catch (error) {
      set({
        error: error.response?.data?.error || 'Login failed',
        isLoading: false,
      });
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      set({ user: null, token: null });
      return;
    }

    try {
      const response = await api.get('/auth/me');
      set({ user: response.data, token });
    } catch (error) {
      localStorage.removeItem('token');
      set({ user: null, token: null });
    }
  },

  updateProfile: async (username, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.put('/auth/me', { username, password });
      set({
        user: response.data.user,
        isLoading: false,
      });
      return true;
    } catch (error) {
      set({
        error: error.response?.data?.error || 'Update failed',
        isLoading: false,
      });
      return false;
    }
  },
}));