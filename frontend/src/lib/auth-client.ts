/**
 * Custom Auth Client
 * Manages authentication state and JWT tokens for our custom backend
 */

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";

// Ensure NEXT_PUBLIC_API_URL is set, otherwise provide a helpful error
const API_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_URL) {
  console.warn('NEXT_PUBLIC_API_URL is not set. Please configure it in your environment variables.');
  // In production, this should be set properly. For development fallback:
  if (process.env.NODE_ENV === 'development') {
    console.warn('Using localhost as fallback for development');
  }
}

// Local storage keys
const TOKEN_KEY = "auth_token";
const USER_KEY = "auth_user";

export interface User {
  id: string;
  email: string;
  name: string;
  emailVerified: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface AuthSession {
  user: User;
  token: string;
  expiresAt: string;
}

/**
 * Sign up with email and password
 */
export async function signUp(email: string, password: string, name?: string): Promise<AuthSession> {
  if (typeof window === "undefined") {
    throw new Error("Sign up can only be performed on the client side");
  }

  const response = await fetch(`${API_URL}/api/auth/sign-up/email`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password, name }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Sign up failed");
  }

  const data = await response.json();

  // Store token and user in localStorage
  localStorage.setItem(TOKEN_KEY, data.session.token);
  localStorage.setItem(USER_KEY, JSON.stringify(data.user));

  return data;
}

/**
 * Sign in with email and password
 */
export async function signIn(email: string, password: string): Promise<AuthSession> {
  if (typeof window === "undefined") {
    throw new Error("Sign in can only be performed on the client side");
  }

  const response = await fetch(`${API_URL}/api/auth/sign-in/email`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Sign in failed");
  }

  const data = await response.json();

  // Store token and user in localStorage
  localStorage.setItem(TOKEN_KEY, data.session.token);
  localStorage.setItem(USER_KEY, JSON.stringify(data.user));

  return data;
}

/**
 * Sign out and clear session
 */
export async function signOut(): Promise<void> {
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
}

/**
 * Get current authentication token
 */
export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Get current user from localStorage
 */
export function getCurrentUser(): User | null {
  if (typeof window === "undefined") return null;

  const userStr = localStorage.getItem(USER_KEY);
  if (!userStr) return null;

  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getAuthToken() !== null && getCurrentUser() !== null;
}

/**
 * React hook for authentication state
 */
export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true); // Always start with loading state to prevent hydration mismatch

  useEffect(() => {
    // Only run on client side
    if (typeof window !== 'undefined') {
      // Check localStorage for existing session
      const token = getAuthToken();
      const storedUser = getCurrentUser();

      if (token && storedUser) {
        setUser(storedUser);
      }
    }

    // Set loading to false after checking
    setLoading(false);
  }, []);

  return {
    user,
    loading,
    isAuthenticated: user !== null && typeof window !== 'undefined',
  };
}

/**
 * React hook for logout functionality
 * Clears authentication data, React Query cache, and navigates to login
 */
export function useLogout() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return async () => {
    if (typeof window !== "undefined") {
      // Clear localStorage (with error handling)
      try {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
      } catch (error) {
        console.warn("Failed to clear localStorage during logout:", error);
        // Continue with logout flow even if localStorage fails
      }
    }

    // Clear React Query cache to prevent data leakage
    queryClient.clear();

    // Navigate to login page
    router.push("/login");
  };
}