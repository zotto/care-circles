/**
 * Authentication Store
 * 
 * Manages authentication state and user session.
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User, Session } from '@supabase/supabase-js';
import * as authService from '@/services/auth';
import * as storage from '@/services/storage';

// Rate limit state management
const RATE_LIMIT_STORAGE_KEY = 'magic_link_rate_limit';
const DEFAULT_RATE_LIMIT_MS = 3600000; // 1 hour (Supabase's typical email rate limit)

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const session = ref<Session | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const isInitialized = ref(false);
  const rateLimitUntil = ref<number | null>(null);
  let authSubscription: ReturnType<typeof authService.onAuthStateChange> | null = null;
  let initializationPromise: Promise<void> | null = null;

  // Computed
  const isAuthenticated = computed(() => !!session.value && !!user.value);
  const accessToken = computed(() => session.value?.access_token ?? null);
  const isRateLimited = computed(() => {
    return rateLimitUntil.value !== null && rateLimitUntil.value > Date.now();
  });
  const rateLimitRemainingSeconds = computed(() => {
    if (!rateLimitUntil.value || rateLimitUntil.value <= Date.now()) {
      return 0;
    }
    return Math.ceil((rateLimitUntil.value - Date.now()) / 1000);
  });

  // Rate limit management
  function loadRateLimitState() {
    try {
      const stored = localStorage.getItem(RATE_LIMIT_STORAGE_KEY);
      if (stored) {
        const until = parseInt(stored, 10);
        if (until > Date.now()) {
          rateLimitUntil.value = until;
        } else {
          clearRateLimitState();
        }
      }
    } catch (err) {
      console.error('Error loading rate limit state:', err);
    }
  }

  function saveRateLimitState(until: number) {
    rateLimitUntil.value = until;
    try {
      localStorage.setItem(RATE_LIMIT_STORAGE_KEY, until.toString());
    } catch (err) {
      console.error('Error saving rate limit state:', err);
    }
  }

  function clearRateLimitState() {
    rateLimitUntil.value = null;
    try {
      localStorage.removeItem(RATE_LIMIT_STORAGE_KEY);
    } catch (err) {
      console.error('Error clearing rate limit state:', err);
    }
  }

  function extractRetryAfterMs(error: any): number | null {
    // Try to extract retry-after from error response
    if (error?.response?.headers?.['retry-after']) {
      const retryAfter = parseInt(error.response.headers['retry-after'], 10);
      if (!isNaN(retryAfter)) {
        return retryAfter * 1000; // Convert seconds to milliseconds
      }
    }
    // Check error message for retry information
    if (error?.message) {
      const retryMatch = error.message.match(/retry[_\s-]?after[:\s]+(\d+)/i);
      if (retryMatch) {
        const seconds = parseInt(retryMatch[1], 10);
        if (!isNaN(seconds)) {
          return seconds * 1000;
        }
      }
    }
    return null;
  }

  // Actions
  async function initialize() {
    // Always load rate limit state (even if already initialized)
    loadRateLimitState();
    
    // If already initialized, return immediately
    if (isInitialized.value && authSubscription) {
      return;
    }

    // If initialization is in progress, wait for it
    if (initializationPromise) {
      return initializationPromise;
    }

    // Start new initialization
    initializationPromise = (async () => {
      isLoading.value = true;
      error.value = null;

      try {
        // Get current session from Supabase
        const currentSession = await authService.getCurrentSession();

        if (currentSession) {
          session.value = currentSession;
          user.value = currentSession.user;

          // Save to localStorage
          storage.saveAuthUser({
            id: currentSession.user.id,
            email: currentSession.user.email!,
            full_name: currentSession.user.user_metadata?.full_name,
          });
          storage.saveAccessToken(currentSession.access_token);
        } else {
          // Clear stored data if no session
          clearSession();
        }

        // Only set up listener once
        if (!authSubscription) {
          authSubscription = authService.onAuthStateChange(async (event, newSession) => {
            console.log('Auth state changed:', event);

            if (newSession) {
              session.value = newSession;
              user.value = newSession.user;

              storage.saveAuthUser({
                id: newSession.user.id,
                email: newSession.user.email!,
                full_name: newSession.user.user_metadata?.full_name,
              });
              storage.saveAccessToken(newSession.access_token);
            } else {
              clearSession();
            }
          });
        }

        isInitialized.value = true;
      } catch (err: any) {
        console.error('Error initializing auth:', err);
        error.value = err.message || 'Failed to initialize authentication';
        clearSession();
      } finally {
        isLoading.value = false;
        initializationPromise = null;
      }
    })();

    return initializationPromise;
  }

  async function signInWithMagicLink(email: string) {
    // Check if we're rate limited
    if (isRateLimited.value) {
      const remaining = rateLimitRemainingSeconds.value;
      const errorMsg = `Too many requests. Please wait ${remaining} second${remaining !== 1 ? 's' : ''} before trying again.`;
      error.value = errorMsg;
      throw new Error(errorMsg);
    }

    isLoading.value = true;
    error.value = null;

    try {
      await authService.signInWithMagicLink(email);
      // Success - clear any previous rate limit
      clearRateLimitState();
    } catch (err: any) {
      console.error('Error sending magic link:', err);
      
      // Check if it's a rate limit error
      const isRateLimit = 
        err.status === 429 ||
        err.statusCode === 429 ||
        err.message?.toLowerCase().includes('rate limit') ||
        err.message?.toLowerCase().includes('too many requests') ||
        err.message?.toLowerCase().includes('email rate limit');

      if (isRateLimit) {
        // Try to extract retry-after from error, otherwise use default
        const retryAfterMs = extractRetryAfterMs(err) || DEFAULT_RATE_LIMIT_MS;
        const cooldownUntil = Date.now() + retryAfterMs;
        saveRateLimitState(cooldownUntil);
        
        const remainingSeconds = Math.ceil(retryAfterMs / 1000);
        const errorMsg = `Too many requests. Please wait ${remainingSeconds} second${remainingSeconds !== 1 ? 's' : ''} before trying again.`;
        error.value = errorMsg;
      } else {
        error.value = err.message || 'Failed to send magic link';
      }
      
      // Re-throw with original error to preserve status code and other properties
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function signOut() {
    isLoading.value = true;
    error.value = null;

    try {
      await authService.signOut();
      clearSession();
    } catch (err: any) {
      console.error('Error signing out:', err);
      error.value = err.message || 'Failed to sign out';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function clearSession() {
    user.value = null;
    session.value = null;
    storage.clearAuthStorage();
  }

  function clearError() {
    error.value = null;
  }

  function cleanup() {
    // Unsubscribe from auth state changes
    if (authSubscription) {
      authSubscription.unsubscribe();
      authSubscription = null;
    }
    isInitialized.value = false;
  }

  return {
    // State
    user,
    session,
    isLoading,
    error,
    isInitialized,
    rateLimitUntil,

    // Computed
    isAuthenticated,
    accessToken,
    isRateLimited,
    rateLimitRemainingSeconds,

    // Actions
    initialize,
    signInWithMagicLink,
    signOut,
    clearSession,
    clearError,
    cleanup,
    clearRateLimitState,
  };
});
