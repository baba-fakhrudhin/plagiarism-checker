import React, { useState } from 'react';
import  uploadApi  from '../api/uploadApi';

export default function FileUpload({ onUploadSuccess }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadMode, setUploadMode] = useState('file'); // 'file' or 'text'
  const [text, setText] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleFileUpload = async (file) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await uploadApi.uploadDocument(file);

      onUploadSuccess(response.document);

    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextUpload = async () => {
    if (!text.trim()) {
      setError('Please enter some text');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await uploadApi.uploadText(text, 'Submitted Text');
      onUploadSuccess(response.document);
      setText('');
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-8 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Upload Document</h2>

      {/* Mode Selector */}
      <div className="flex space-x-4 mb-6">
        <button
          onClick={() => setUploadMode('file')}
          className={`px-6 py-2 rounded-lg font-semibold transition ${
            uploadMode === 'file'
              ? 'bg-primary text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Upload File
        </button>
        <button
          onClick={() => setUploadMode('text')}
          className={`px-6 py-2 rounded-lg font-semibold transition ${
            uploadMode === 'text'
              ? 'bg-primary text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Paste Text
        </button>
      </div>

      {error && (
        <div className="bg-danger/10 border border-danger text-danger rounded-lg p-4 mb-4">
          {error}
        </div>
      )}

      {uploadMode === 'file' ? (
        // File Upload Section
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-12 text-center transition ${
            dragActive
              ? 'border-primary bg-primary/5'
              : 'border-gray-300 hover:border-primary'
          }`}
        >
          <svg
            className="w-16 h-16 mx-auto mb-4 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          <p className="text-gray-600 mb-2">Drag and drop your file here</p>
          <p className="text-gray-500 text-sm mb-4">or</p>
          <input
            type="file"
            id="file-input"
            className="hidden"
            onChange={(e) => e.target.files && handleFileUpload(e.target.files[0])}
            accept=".txt,.pdf,.docx,.pptx,.doc,.ppt"
          />
          <label
            htmlFor="file-input"
            className="bg-primary text-white px-6 py-2 rounded-lg cursor-pointer hover:bg-secondary transition inline-block"
          >
            Select File
          </label>
          <p className="text-gray-500 text-xs mt-4">
            Supported: TXT, PDF, DOCX, PPTX (Max 50MB)
          </p>
        </div>
      ) : (
        // Text Upload Section
        <div>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste your text here..."
            className="w-full h-64 border border-gray-300 rounded-lg p-4 focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <div className="mt-4 text-sm text-gray-600">
            {text.length} / 50000 characters
          </div>
          <button
            onClick={handleTextUpload}
            disabled={isLoading || !text.trim()}
            className="mt-4 w-full bg-primary text-white py-2 rounded-lg hover:bg-secondary transition disabled:bg-gray-400 font-semibold"
          >
            {isLoading ? 'Processing...' : 'Analyze Text'}
          </button>
        </div>
      )}

      {isLoading && (
        <div className="mt-4 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          <p className="mt-2 text-gray-600">Processing your file...</p>
        </div>
      )}
    </div>
  );
}