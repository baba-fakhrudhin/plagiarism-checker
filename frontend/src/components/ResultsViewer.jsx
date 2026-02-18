import React from "react";
import { Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function ResultsViewer({ results }) {
  if (!results) return null;

  const matches = results.plagiarism_matches || [];
  const plagiarismScore = results.plagiarism_score || 0;
  const aiProbability = results.ai_probability || 0;

  const getSimilarityColor = (score) => {
    if (score >= 0.8) return "text-red-600";
    if (score >= 0.6) return "text-yellow-600";
    return "text-green-600";
  };

  const plagiarismChart = {
    labels: ["Plagiarized", "Original"],
    datasets: [
      {
        data: [
          (plagiarismScore * 100).toFixed(1),
          ((1 - plagiarismScore) * 100).toFixed(1),
        ],
        backgroundColor: ["#ef4444", "#10b981"],
      },
    ],
  };

  const aiChart = {
    labels: ["AI Generated", "Human Written"],
    datasets: [
      {
        data: [
          (aiProbability * 100).toFixed(1),
          ((1 - aiProbability) * 100).toFixed(1),
        ],
        backgroundColor: ["#f59e0b", "#10b981"],
      },
    ],
  };

  return (
    <div className="space-y-6">

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm font-semibold mb-2">
            Plagiarism Score
          </h3>
          <p className={`text-4xl font-bold ${getSimilarityColor(plagiarismScore)}`}>
            {(plagiarismScore * 100).toFixed(1)}%
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm font-semibold mb-2">
            Matches Found
          </h3>
          <p className="text-4xl font-bold text-primary">
            {matches.length}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm font-semibold mb-2">
            AI Probability
          </h3>
          <p className="text-4xl font-bold text-orange-500">
            {(aiProbability * 100).toFixed(1)}%
          </p>
        </div>

      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">
            Plagiarism Analysis
          </h3>
          <Doughnut data={plagiarismChart} />
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">
            AI Detection
          </h3>
          <Doughnut data={aiChart} />
        </div>

      </div>

      {/* Matches */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">
          Matches ({matches.length})
        </h3>

        <div className="space-y-3 max-h-96 overflow-y-auto">
          {matches.map((match, idx) => (
            <div
              key={idx}
              className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
            >
              <div className="flex justify-between items-start mb-2">
                <span className="text-xs font-semibold px-2 py-1 rounded bg-yellow-100 text-yellow-800">
                  Semantic
                </span>
                <span className={`text-sm font-bold ${getSimilarityColor(match.similarity_score)}`}>
                  {(match.similarity_score * 100).toFixed(1)}% Match
                </span>
              </div>

              <p className="text-sm text-gray-700 mb-2">
                <strong>Matched Text:</strong>{" "}
                "{match.matched_text?.substring(0, 150)}..."
              </p>

              {match.source_url && (
                <a
                  href={match.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary text-sm hover:underline"
                >
                  → View Source
                </a>
              )}
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
