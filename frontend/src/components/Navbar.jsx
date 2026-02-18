import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export default function Navbar() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-primary text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 font-bold text-xl">
            <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
              <span className="text-primary font-bold">PC</span>
            </div>
            <span>PlagiarismChecker</span>
          </Link>

          {/* Navigation Links */}
          {user && (
            <div className="flex items-center space-x-6">
              <Link
                to="/upload"
                className="hover:bg-secondary px-3 py-2 rounded-md transition"
              >
                Upload
              </Link>
              <Link
                to="/profile"
                className="hover:bg-secondary px-3 py-2 rounded-md transition"
              >
                Profile
              </Link>
              <button
                onClick={handleLogout}
                className="bg-danger hover:bg-red-700 px-4 py-2 rounded-md transition"
              >
                Logout
              </button>
              <span className="text-gray-200">{user.username}</span>
            </div>
          )}

          {!user && (
            <div className="flex items-center space-x-4">
              <Link
                to="/login"
                className="hover:bg-secondary px-3 py-2 rounded-md transition"
              >
                Login
              </Link>
              <Link
                to="/signup"
                className="bg-accent text-primary font-bold px-4 py-2 rounded-md hover:bg-yellow-500 transition"
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}