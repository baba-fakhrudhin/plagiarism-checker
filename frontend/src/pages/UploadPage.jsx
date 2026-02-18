import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import FileUpload from "../components/FileUpload";
import analysisApi from "../api/analysisApi";

export default function UploadPage() {
  const [document, setDocument] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const navigate = useNavigate();

  const handleUploadSuccess = (uploadedDoc) => {
    setDocument(uploadedDoc);
  };

  const handleStartAnalysis = async () => {
    if (!document) return;

    setIsAnalyzing(true);

    try {
      const response = await analysisApi.startAnalysis(document.id);

      // response is already response.data
      const analysisId =
        response.analysis?.id || response.id;

      if (analysisId) {
        navigate(`/results/${analysisId}`);
      } else {
        alert("Invalid analysis response from server");
        setIsAnalyzing(false);
      }
    } catch (error) {
      alert(
        "Error starting analysis: " +
          (error.response?.data?.error || "Server error")
      );
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <h1 className="text-4xl font-bold text-gray-800 mb-8">
        Upload & Analyze
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <FileUpload onUploadSuccess={handleUploadSuccess} />
        </div>

        {document && (
          <div className="bg-white rounded-lg shadow p-6 h-fit sticky top-20">
            <h2 className="text-xl font-bold mb-4 text-gray-800">
              Document Ready
            </h2>

            <div className="space-y-3 mb-6">
              <div>
                <p className="text-sm text-gray-600">Filename</p>
                <p className="font-semibold text-gray-800">
                  {document.filename}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-600">Type</p>
                <p className="font-semibold text-gray-800">
                  {document.file_type?.toUpperCase()}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-600">Size</p>
                <p className="font-semibold text-gray-800">
                  {(document.file_size / 1024).toFixed(2)} KB
                </p>
              </div>
            </div>

            <button
              onClick={handleStartAnalysis}
              disabled={isAnalyzing}
              className="w-full bg-primary text-white py-3 rounded-lg font-semibold hover:bg-secondary transition disabled:bg-gray-400"
            >
              {isAnalyzing ? "Analyzing..." : "Start Analysis"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
