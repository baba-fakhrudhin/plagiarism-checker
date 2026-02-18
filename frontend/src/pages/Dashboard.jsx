import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import uploadApi from '../api/uploadApi';
import analysisApi from '../api/analysisApi';

export default function Dashboard() {
  const [documents, setDocuments] = useState([]);
  const [analyses, setAnalyses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [docsRes, analysesRes] = await Promise.all([
       uploadApi.listDocuments(1) ,
        analysisApi.listAnalyses(1, 5),
      ]);
      setDocuments(docsRes.documents || []);  
      setAnalyses(analysesRes.analyses || []);

    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">Dashboard</h1>
        <p className="text-gray-600 mb-8">
          Welcome! Upload documents to check for plagiarism.
        </p>
        <Link
          to="/upload"
          className="bg-primary text-white px-6 py-3 rounded-lg font-semibold hover:bg-secondary transition inline-block"
        >
          + Upload Document
        </Link>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Documents */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4 text-gray-800">Recent Documents</h2>
            {documents.length === 0 ? (
              <p className="text-gray-600">No documents uploaded yet</p>
            ) : (
              <div className="space-y-3">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold text-gray-800">{doc.filename}</h3>
                        <p className="text-sm text-gray-600">
                          {(doc.file_size / 1024).toFixed(2)} KB
                        </p>
                      </div>
                      <span className="text-xs text-gray-500">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Analyses */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4 text-gray-800">Recent Analyses</h2>
            {analyses.length === 0 ? (
              <p className="text-gray-600">No analyses yet</p>
            ) : (
              <div className="space-y-3">
                {analyses.map((analysis) => (
                  <Link
                    key={analysis.id}
                    to={`/results/${analysis.id}`}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 hover:shadow-md transition block"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-semibold text-gray-800">
                          Similarity: {(analysis.plagiarism_score* 100).toFixed(1)}%
                        </p>
                        <span className={`text-xs font-semibold px-2 py-1 rounded inline-block mt-2 ${getStatusBadge(analysis.status)}`}>
                          {analysis.status}
                        </span>
                      </div>
                      <span className="text-xs text-gray-500">
                        {new Date(analysis.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}