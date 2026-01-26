/**
 * LocalStorage Utilities
 * 
 * Helper functions for managing localStorage.
 */

const STORAGE_KEYS = {
  AUTH_USER: 'care_circles_auth_user',
  AUTH_TOKEN: 'care_circles_auth_token',
} as const;

export interface StoredAuthUser {
  id: string;
  email: string;
  full_name?: string;
}

/**
 * Save auth user to localStorage
 */
export function saveAuthUser(user: StoredAuthUser): void {
  try {
    localStorage.setItem(STORAGE_KEYS.AUTH_USER, JSON.stringify(user));
  } catch (error) {
    console.error('Failed to save auth user to localStorage:', error);
  }
}

/**
 * Get auth user from localStorage
 */
export function getAuthUser(): StoredAuthUser | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.AUTH_USER);
    return stored ? JSON.parse(stored) : null;
  } catch (error) {
    console.error('Failed to get auth user from localStorage:', error);
    return null;
  }
}

/**
 * Remove auth user from localStorage
 */
export function removeAuthUser(): void {
  try {
    localStorage.removeItem(STORAGE_KEYS.AUTH_USER);
  } catch (error) {
    console.error('Failed to remove auth user from localStorage:', error);
  }
}

/**
 * Save access token to localStorage
 */
export function saveAccessToken(token: string): void {
  try {
    localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
  } catch (error) {
    console.error('Failed to save access token to localStorage:', error);
  }
}

/**
 * Get access token from localStorage
 */
export function getAccessToken(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
  } catch (error) {
    console.error('Failed to get access token from localStorage:', error);
    return null;
  }
}

/**
 * Remove access token from localStorage
 */
export function removeAccessToken(): void {
  try {
    localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
  } catch (error) {
    console.error('Failed to remove access token from localStorage:', error);
  }
}

/**
 * Clear all auth data from localStorage
 */
export function clearAuthStorage(): void {
  removeAuthUser();
  removeAccessToken();
}
