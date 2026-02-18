import apiClient from "./client";

export const startAnalysis = async (documentId) => {
  const response = await apiClient.post("/analysis/start", {
    document_id: documentId,
  });

  return response.data;
};

export const checkAnalysisStatus = async (analysisId) => {
  const response = await apiClient.get(
    `/analysis/status/${analysisId}`
  );
  return response.data;
};

export const listAnalyses = async (page = 1) => {
  const response = await apiClient.get(
    `/analysis/list?page=${page}`
  );
  return response.data;
};
