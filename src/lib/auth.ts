/** Minimal client auth helpers around the existing backend JWT auth. */

const ACCESS_KEY = "smartllm_access_token";
const REFRESH_KEY = "smartllm_refresh_token";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(ACCESS_KEY);
}

export function isAuthenticated(): boolean {
  return Boolean(getAccessToken());
}

export function setSessionTokens(accessToken: string, refreshToken: string): void {
  sessionStorage.setItem(ACCESS_KEY, accessToken);
  sessionStorage.setItem(REFRESH_KEY, refreshToken);
}

export function clearSession(): void {
  sessionStorage.removeItem(ACCESS_KEY);
  sessionStorage.removeItem(REFRESH_KEY);
}
