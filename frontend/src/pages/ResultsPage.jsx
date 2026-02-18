import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import analysisApi from '../api/analysisApi';
import ResultsViewer from '../components/ResultsViewer';
import HighlightedText from '../components/HighlightedText';

export default function ResultsPage() {
  const { analysisId } = useParams();
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('analysis');

  useEffect(() => {
    loadResults();
    const interval = setInterval(checkStatus, 2000);
    return () => clearInterval(interval);
  }, [analysisId]);

  const checkStatus = async () => {
    try {
      const response = await analysisApi.checkStatus(analysisId);
      if (response.data.status === 'completed') {
        loadResults();
      }
    } catch (error) {
      console.error('Error checking status:', error);
    }
  };

  const loadResults = async () => {
    try {
      const response = await analysisApi.getResults(analysisId);
      setResults(response.data);
      setIsLoading(false);
    } catch (error) {
      if (error.response?.status === 400) {
        // Still processing
        console.log('Still processing...');
      } else {
        setError(error.response?.data?.error || 'Error loading results');
        setIsLoading(false);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          <p className="mt-4 text-gray-600">Analyzing your document...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="bg-danger/10 border border-danger text-danger rounded-lg p-4">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <h1 className="text-4xl font-bold text-gray-800 mb-2">Analysis Results</h1>
      <p className="text-gray-600 mb-8">Document: {results.document.filename}</p>

      {/* Tabs */}
      <div className="flex space-x-4 mb-6 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('analysis')}
          className={`px-4 py-2 font-semibold transition ${
            activeTab === 'analysis'
              ? 'text-primary border-b-2 border-primary'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Analysis
        </button>
        <button
          onClick={() => setActiveTab('text')}
          className={`px-4 py-2 font-semibold transition ${
            activeTab === 'text'
              ? 'text-primary border-b-2 border-primary'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Highlighted Text
        </button>
      </div>

      {/* Content */}
      {activeTab === 'analysis' ? (
        <ResultsViewer results={results} />
      ) : (
        <HighlightedText text={results.document.content} highlights={results.highlighted_segments} />
      )}
    </div>
  );
}