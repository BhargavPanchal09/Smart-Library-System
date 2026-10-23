import { auth } from "./firebase";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

export async function fetchFromAPI(endpoint: string, options: RequestInit = {}) {
  if (process.env.NODE_ENV === "production" && !process.env.NEXT_PUBLIC_API_BASE_URL) {
    throw new Error("Configure NEXT_PUBLIC_API_BASE_URL before building for production.");
  }
  const formattedEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  await auth.authStateReady();
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  if (auth.currentUser) headers.set("Authorization", `Bearer ${await auth.currentUser.getIdToken()}`);
  const response = await fetch(`${API_BASE_URL}${formattedEndpoint}`, { ...options, headers });
  if (!response.ok) throw new Error(`API call failed: ${response.status}`);
  return response.json();
}
