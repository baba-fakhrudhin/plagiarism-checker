import apiClient from "./client";

export const signup = async (data) => {
  const response = await apiClient.post("/auth/signup", data);
  return response.data;
};

export const login = async (data) => {
  const response = await apiClient.post("/auth/login", data);
  return response.data;
};

export const getProfile = async () => {
  const response = await apiClient.get("/auth/me");
  return response.data;
};

export const updateProfile = async (data) => {
  const response = await apiClient.put("/auth/me", data);
  return response.data;
};

export const logout = async () => {
  const response = await apiClient.post("/auth/logout");
  return response.data;
};
