'use client';

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { signIn } from "@/lib/auth-client";

export default function LoginForm() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");

    // Client-side validation
    if (!email || !password) {
      setError("Email and password are required");
      return;
    }

    setLoading(true);

    try {
      // Attempt signin with custom auth client
      await signIn(email, password);

      // Login successful - redirect to tasks page (FR-004, T033)
      router.push("/tasks");
    } catch (err: any) {
      // Handle login errors (FR-003: incorrect credentials)
      if (err.message?.includes("credentials") || err.message?.includes("password")) {
        setError("Incorrect email or password. Please try again.");
      } else if (err.message?.includes("not found")) {
        setError("Account not found. Please sign up first.");
      } else {
        setError(err.message || "Failed to sign in. Please try again.");
      }
      setLoading(false);
    }
  };

  return (
    <div className="auth-form card bg-white/10 backdrop-blur-lg border border-white/20 shadow-xl">
      <div className="text-center mb-lg">
        <div className="flex justify-center mb-md">
          <div className="bg-primary-100/30 p-md rounded-full backdrop-blur-sm">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-primary-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="40" height="40">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
        </div>
        <h1 className="mb-md text-white">Welcome Back</h1>
        <p className="text-secondary-200">Sign in to access your tasks</p>
      </div>

      <form onSubmit={handleSubmit} className="w-full">
        {error && (
          <div className="error-message mb-lg bg-red-500/20 border border-red-400/30 text-red-100 backdrop-blur-sm">
            {error}
          </div>
        )}

        <div className="form-group mb-lg">
          <label htmlFor="email" className="form-label mb-sm text-secondary-200">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
            disabled={loading}
            autoComplete="email"
            className="form-input w-full bg-white/20 border-white/30 text-white placeholder:text-white/60 focus:border-primary-300 focus:ring focus:ring-primary-300/50"
          />
        </div>

        <div className="form-group mb-lg">
          <label htmlFor="password" className="form-label mb-sm text-secondary-200">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            required
            disabled={loading}
            autoComplete="current-password"
            className="form-input w-full bg-white/20 border-white/30 text-white placeholder:text-white/60 focus:border-primary-300 focus:ring focus:ring-primary-300/50"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn btn-primary w-full py-3 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5"
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Signing In...
            </>
          ) : "Sign In"}
        </button>
      </form>

      <div className="mt-lg text-center">
        <p className="text-secondary-200">
          Don't have an account?{" "}
          <a href="/signup" className="text-primary-300 font-medium hover:text-primary-200 transition-colors">
            Sign up
          </a>
        </p>
      </div>
    </div>
  );
}