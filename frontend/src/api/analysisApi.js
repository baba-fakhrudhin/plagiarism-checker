import apiClient from "./client";

const analysisApi = {
  startAnalysis: async (documentId) => {
    const response = await apiClient.post("/analysis/start", {
      document_id: documentId,
    });
    return response.data;
  },

  getStatus: async (analysisId) => {
    const response = await apiClient.get(`/analysis/status/${analysisId}`);
    return response.data;
  },

  listAnalyses: async () => {
    const response = await apiClient.get("/analysis/list");
    return response.data;
  },
};

export default analysisApi;
