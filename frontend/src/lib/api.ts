/**
 * API Client
 * Wrapper for backend API requests with JWT attachment
 */

import { getAuthToken, signOut, getCurrentUser } from "./auth-client";
import type { Task, TaskCreate, TaskUpdate, TaskCompletionToggle } from "../types/task";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Helper function to decode JWT token and extract user ID
function getUserIdFromToken(token: string): string | null {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    const decodedToken = JSON.parse(jsonPayload);
    return decodedToken.sub; // 'sub' field typically contains the user ID in JWT
  } catch (error) {
    console.error('Error decoding JWT token:', error);
    return null;
  }
}

/**
 * Generic API request with JWT authentication
 *
 * Features:
 * - Automatic JWT token attachment (FR-051)
 * - 401 handling: Clear session and redirect to login
 * - 403 handling: Access denied error
 * - Network error handling
 * - JSON parsing
 */
export async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  // Get JWT token from localStorage
  const token = getAuthToken();

  if (!token) {
    // No token available - redirect to login
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new Error("Not authenticated");
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`, // Attach JWT (FR-051)
        ...options?.headers,
      },
    });

    // Handle 401 Unauthorized (token invalid/expired)
    if (response.status === 401) {
      console.error("401 Unauthorized - clearing session");
      await signOut();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      throw new Error("Unauthorized");
    }

    // Handle 403 Forbidden (access denied)
    if (response.status === 403) {
      throw new Error("Access denied");
    }

    // Handle 400 Bad Request (often due to user ID mismatch)
    if (response.status === 400) {
      console.error(`400 Bad Request for endpoint: ${endpoint}`);
      const error = await response.json().catch(() => ({}));
      console.error("Error details:", error);

      // Check if it's a user ID mismatch error
      if (error.detail && error.detail.includes("user")) {
        console.error("User ID in token may not match user ID in URL path");
      }

      throw new Error(error.detail || "Bad Request - please check your authentication");
    }

    // Handle 404 Not Found
    if (response.status === 404) {
      throw new Error("Resource not found");
    }

    // Handle 204 No Content (successful delete)
    if (response.status === 204) {
      return null as T;
    }

    // Handle other error responses
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Request failed with status ${response.status}`);
    }

    // Parse and return JSON response
    return response.json();
  } catch (error) {
    // Re-throw API errors
    if (error instanceof Error) {
      throw error;
    }

    // Network errors
    throw new Error("Network error. Please check your connection and try again.");
  }
}

/**
 * API Client Methods for Tasks
 * Typed methods for task CRUD operations
 */

export const taskApi = {
  /**
   * List all tasks for authenticated user (GET /api/{user_id}/tasks)
   */
  list: async (userId: string): Promise<Task[]> => {
    // Validate that the user ID matches the authenticated user
    const token = getAuthToken();
    if (token) {
      const tokenUserId = getUserIdFromToken(token);
      if (tokenUserId && tokenUserId !== userId) {
        console.warn(`User ID mismatch: token user ID ${tokenUserId} does not match request user ID ${userId}`);
        // Use the token user ID instead of the passed user ID to prevent 400 errors
        console.log(`Using token user ID ${tokenUserId} instead of passed user ID ${userId}`);
        return apiRequest<Task[]>(`/api/${tokenUserId}/tasks`);
      }
    }
    return apiRequest<Task[]>(`/api/${userId}/tasks`);
  },

  /**
   * Create new task (POST /api/{user_id}/tasks)
   */
  create: async (userId: string, data: TaskCreate): Promise<Task> => {
    // Validate that the user ID matches the authenticated user
    const token = getAuthToken();
    if (token) {
      const tokenUserId = getUserIdFromToken(token);
      if (tokenUserId && tokenUserId !== userId) {
        console.warn(`User ID mismatch: token user ID ${tokenUserId} does not match request user ID ${userId}`);
        // Use the token user ID instead of the passed user ID to prevent 400 errors
        console.log(`Using token user ID ${tokenUserId} instead of passed user ID ${userId}`);
        return apiRequest<Task>(`/api/${tokenUserId}/tasks`, {
          method: "POST",
          body: JSON.stringify(data),
        });
      }
    }
    return apiRequest<Task>(`/api/${userId}/tasks`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  /**
   * Get specific task (GET /api/{user_id}/tasks/{id})
   */
  get: async (userId: string, taskId: number): Promise<Task> => {
    // Validate that the user ID matches the authenticated user
    const token = getAuthToken();
    if (token) {
      const tokenUserId = getUserIdFromToken(token);
      if (tokenUserId && tokenUserId !== userId) {
        console.warn(`User ID mismatch: token user ID ${tokenUserId} does not match request user ID ${userId}`);
        // Use the token user ID instead of the passed user ID to prevent 400 errors
        console.log(`Using token user ID ${tokenUserId} instead of passed user ID ${userId}`);
        return apiRequest<Task>(`/api/${tokenUserId}/tasks/${taskId}`);
      }
    }
    return apiRequest<Task>(`/api/${userId}/tasks/${taskId}`);
  },

  /**
   * Update task (PUT /api/{user_id}/tasks/{id})
   */
  update: async (userId: string, taskId: number, data: TaskUpdate): Promise<Task> => {
    // Validate that the user ID matches the authenticated user
    const token = getAuthToken();
    if (token) {
      const tokenUserId = getUserIdFromToken(token);
      if (tokenUserId && tokenUserId !== userId) {
        console.warn(`User ID mismatch: token user ID ${tokenUserId} does not match request user ID ${userId}`);
        // Use the token user ID instead of the passed user ID to prevent 400 errors
        console.log(`Using token user ID ${tokenUserId} instead of passed user ID ${userId}`);
        return apiRequest<Task>(`/api/${tokenUserId}/tasks/${taskId}`, {
          method: "PUT",
          body: JSON.stringify(data),
        });
      }
    }
    return apiRequest<Task>(`/api/${userId}/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete task (DELETE /api/{user_id}/tasks/{id})
   */
  delete: async (userId: string, taskId: number): Promise<void> => {
    // Validate that the user ID matches the authenticated user
    const token = getAuthToken();
    if (token) {
      const tokenUserId = getUserIdFromToken(token);
      if (tokenUserId && tokenUserId !== userId) {
        console.warn(`User ID mismatch: token user ID ${tokenUserId} does not match request user ID ${userId}`);
        // Use the token user ID instead of the passed user ID to prevent 400 errors
        console.log(`Using token user ID ${tokenUserId} instead of passed user ID ${userId}`);
        return apiRequest<void>(`/api/${tokenUserId}/tasks/${taskId}`, {
          method: "DELETE",
        });
      }
    }
    return apiRequest<void>(`/api/${userId}/tasks/${taskId}`, {
      method: "DELETE",
    });
  },

  /**
   * Toggle task completion (PATCH /api/{user_id}/tasks/{id}/complete)
   */
  toggleComplete: async (
    userId: string,
    taskId: number,
    data: TaskCompletionToggle
  ): Promise<Task> => {
    // Validate that the user ID matches the authenticated user
    const token = getAuthToken();
    if (token) {
      const tokenUserId = getUserIdFromToken(token);
      if (tokenUserId && tokenUserId !== userId) {
        console.warn(`User ID mismatch: token user ID ${tokenUserId} does not match request user ID ${userId}`);
        // Use the token user ID instead of the passed user ID to prevent 400 errors
        console.log(`Using token user ID ${tokenUserId} instead of passed user ID ${userId}`);
        return apiRequest<Task>(`/api/${tokenUserId}/tasks/${taskId}/complete`, {
          method: "PATCH",
          body: JSON.stringify(data),
        });
      }
    }
    return apiRequest<Task>(`/api/${userId}/tasks/${taskId}/complete`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },
};
