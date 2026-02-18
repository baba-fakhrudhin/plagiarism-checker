import React from "react";
import { useAuthStore } from "../store/authStore";

export default function ProfilePage() {
  const { user, logout } = useAuthStore();

  if (!user) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <p className="text-gray-600">Loading profile...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        Profile
      </h1>

      <div className="bg-white rounded-lg shadow p-6 space-y-4">
        <div>
          <p className="text-sm text-gray-600">Username</p>
          <p className="font-semibold text-gray-800">
            {user.username}
          </p>
        </div>

        <div>
          <p className="text-sm text-gray-600">Email</p>
          <p className="font-semibold text-gray-800">
            {user.email}
          </p>
        </div>

        <button
          onClick={logout}
          className="mt-4 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition"
        >
          Logout
        </button>
      </div>
    </div>
  );
}
