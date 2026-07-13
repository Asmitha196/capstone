/**
 * Global API Client Helper.
 * Handles automatic auth header insertion, JSON serialization, and response code checks.
 */

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

interface FetchOptions extends RequestInit {
  json?: any;
}

export async function apiFetch(endpoint: string, options: FetchOptions = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Setup headers
  const headers = new Headers(options.headers || {});
  
  // Set json body content type if payload exists
  if (options.json) {
    headers.set("Content-Type", "application/json");
    options.body = JSON.stringify(options.json);
  }

  // Set Authorization header if token exists in localStorage
  const token = localStorage.getItem("token");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const fetchOptions: RequestInit = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, fetchOptions);

    // Handle 204 No Content
    if (response.status === 204) {
      return null;
    }

    // Handle session expiry / unauthorized
    if (response.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      // Force reload to redirect to login page
      if (window.location.pathname !== "/login" && window.location.pathname !== "/register") {
        window.location.href = "/login";
      }
      throw new Error("Unauthorized access. Token expired.");
    }

    const data = await response.json();

    if (!response.ok) {
      const errorMsg = data.detail || data.message || "An error occurred during network request.";
      throw new Error(errorMsg);
    }

    return data;
  } catch (error: any) {
    console.error(`API Fetch Error on ${endpoint}:`, error);
    throw error;
  }
}
