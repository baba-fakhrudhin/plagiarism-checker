import apiClient from "./client";

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.post("/upload/document", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};

export const uploadText = async (text, title = "Untitled") => {
  const response = await apiClient.post("/upload/text", {
    text,
    title,
  });

  return response.data;
};

export const listDocuments = async (page = 1) => {
  const response = await apiClient.get(`/upload/documents?page=${page}`);
  return response.data;
};

export const getDocument = async (id) => {
  const response = await apiClient.get(`/upload/document/${id}`);
  return response.data;
};

export const deleteDocument = async (id) => {
  const response = await apiClient.delete(`/upload/document/${id}`);
  return response.data;
};
const uploadApi = {
  uploadDocument,
  uploadText,
  listDocuments,
  getDocument,
  deleteDocument,
};

export default uploadApi;