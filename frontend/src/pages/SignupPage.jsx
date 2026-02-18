import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuthStore } from "../store/authStore";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const { signup, isLoading, error } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    const result = await signup(email, username, password);

    if (result.success) {
      navigate("/", { replace: true });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center">Sign Up</h1>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full border px-3 py-2 rounded"
          />

          <input
            type="text"
            placeholder="Username"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full border px-3 py-2 rounded"
          />

          <input
            type="password"
            placeholder="Password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border px-3 py-2 rounded"
          />

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-primary text-white py-2 rounded disabled:bg-gray-400"
          >
            {isLoading ? "Creating..." : "Sign Up"}
          </button>
        </form>

        <p className="text-center mt-4 text-sm">
          Already have an account?{" "}
          <Link to="/login" className="text-primary">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}
