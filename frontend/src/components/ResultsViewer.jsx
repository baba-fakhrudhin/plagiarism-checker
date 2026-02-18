import React, { useState } from 'react';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

export default function ResultsViewer({ results }) {
  const [filterType, setFilterType] = useState('all');
  const [minSimilarity, setMinSimilarity] = useState(0);

  const filteredMatches = results.matches.filter((match) => {
    const typeMatch = filterType === 'all' || match.match_type === filterType;
    const similarityMatch = match.similarity_score >= minSimilarity;
    return typeMatch && similarityMatch;
  });

  const getSimilarityColor = (score) => {
    if (score >= 0.8) return 'text-danger';
    if (score >= 0.6) return 'text-warning';
    return 'text-warning';
  };

  const getMatchTypeBadge = (type) => {
    const colors = {
      exact: 'bg-red-100 text-red-800',
      semantic: 'bg-yellow-100 text-yellow-800',
      paraphrase: 'bg-orange-100 text-orange-800',
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  const chartData = {
    labels: ['Plagiarized', 'Original'],
    datasets: [
      {
        data: [
          (results.overall_similarity * 100).toFixed(1),
          ((1 - results.overall_similarity) * 100).toFixed(1),
        ],
        backgroundColor: ['#ef4444', '#10b981'],
        borderColor: ['#991b1b', '#065f46'],
        borderWidth: 2,
      },
    ],
  };

  const aiChartData = {
    labels: ['AI Generated', 'Human Written'],
    datasets: [
      {
        data: [
          (results.ai_generated_probability * 100).toFixed(1),
          ((1 - results.ai_generated_probability) * 100).toFixed(1),
        ],
        backgroundColor: ['#f59e0b', '#10b981'],
        borderColor: ['#b45309', '#065f46'],
        borderWidth: 2,
      },
    ],
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm font-semibold mb-2">Similarity Score</h3>
          <p className={`text-4xl font-bold ${getSimilarityColor(results.overall_similarity)}`}>
            {(results.overall_similarity * 100).toFixed(1)}%
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm font-semibold mb-2">Plagiarism Matches</h3>
          <p className="text-4xl font-bold text-primary">{results.total_matches}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm font-semibold mb-2">AI Generated Probability</h3>
          <p className="text-4xl font-bold text-accent">
            {(results.ai_generated_probability * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Plagiarism Analysis</h3>
          <Doughnut data={chartData} options={{ responsive: true }} />
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">AI Detection</h3>
          <Doughnut data={aiChartData} options={{ responsive: true }} />
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-800">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Match Type
            </label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="all">All Types</option>
              <option value="exact">Exact Matches</option>
              <option value="semantic">Semantic Matches</option>
              <option value="paraphrase">Paraphrases</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Minimum Similarity: {(minSimilarity * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={minSimilarity}
              onChange={(e) => setMinSimilarity(parseFloat(e.target.value))}
              className="w-full"
            />
          </div>
        </div>
      </div>

      {/* Matches List */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-800">
          Matches ({filteredMatches.length})
        </h3>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {filteredMatches.map((match, idx) => (
            <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
              <div className="flex justify-between items-start mb-2">
                <span className={`text-xs font-semibold px-2 py-1 rounded ${getMatchTypeBadge(match.match_type)}`}>
                  {match.match_type.toUpperCase()}
                </span>
                <span className={`text-sm font-bold ${getSimilarityColor(match.similarity_score)}`}>
                  {(match.similarity_score * 100).toFixed(1)}% Match
                </span>
              </div>
              <p className="text-sm text-gray-700 mb-2">
                <strong>Your Text:</strong> "{match.original_text.substring(0, 100)}..."
              </p>
              <p className="text-sm text-gray-700 mb-2">
                <strong>Source Text:</strong> "{match.matched_text.substring(0, 100)}..."
              </p>
              {match.source_url && (
                <a
                  href={match.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary text-sm hover:underline"
                >
                  → {match.source_title || 'View Source'}
                </a>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}