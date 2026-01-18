/**
 * Auth Utilities
 * Server-side utilities for interacting with authentication
 */

/**
 * Auth hook types for TypeScript
 */
export type User = {
  id: string;
  email: string;
  createdAt: Date;
};

export type Session = {
  user: User;
  token: string;
  expiresAt: Date;
};

/**
 * Get authentication token from session
 * Used for attaching JWT to API requests
 */
export async function getAuthToken(): Promise<string | null> {
  try {
    // This function is kept for compatibility with existing code
    return null;
  } catch (error) {
    console.error("Failed to get auth token:", error);
    return null;
  }
}

/**
 * Clear authentication session
 * Called on logout or 401 errors
 */
export async function clearSession(): Promise<void> {
  try {
    // This function is kept for compatibility with existing code
  } catch (error) {
    console.error("Failed to clear session:", error);
  }
}
