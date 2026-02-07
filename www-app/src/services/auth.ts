/**
 * Supabase Authentication Service
 * 
 * Handles user authentication using Supabase magic links.
 */

import { createClient, type SupabaseClient, type Session, type User } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

// Create Supabase client
const supabase: SupabaseClient = createClient(supabaseUrl, supabaseAnonKey);

/**
 * Send magic link to user's email
 */
export async function signInWithMagicLink(email: string): Promise<void> {
  const { error } = await supabase.auth.signInWithOtp({
    email,
    options: {
      emailRedirectTo: `${window.location.origin}/auth/callback`,
    },
  });

  if (error) {
    throw error;
  }
}

/**
 * Sign out current user
 */
export async function signOut(): Promise<void> {
  const { error } = await supabase.auth.signOut();
  
  if (error) {
    throw error;
  }
}

/**
 * Get current session
 */
export async function getCurrentSession(): Promise<Session | null> {
  const { data, error } = await supabase.auth.getSession();
  
  if (error) {
    throw error;
  }
  
  return data.session;
}

/**
 * Get current user
 */
export async function getCurrentUser(): Promise<User | null> {
  const { data, error } = await supabase.auth.getUser();
  
  if (error) {
    throw error;
  }
  
  return data.user;
}

/**
 * Get access token for API calls
 */
export async function getAccessToken(): Promise<string | null> {
  const session = await getCurrentSession();
  return session?.access_token ?? null;
}

/**
 * Listen for auth state changes
 */
export function onAuthStateChange(
  callback: (event: string, session: Session | null) => void
) {
  const { data: { subscription } } = supabase.auth.onAuthStateChange(
    (event, session) => {
      callback(event, session);
    }
  );
  
  return subscription;
}

/**
 * Handle OAuth callback (for magic link redirect)
 * 
 * Supabase magic links redirect with hash fragments that need to be processed.
 * Supabase automatically processes hash fragments when getSession() is called,
 * but we need to wait a bit for the browser to parse the hash first.
 */
export async function handleAuthCallback(): Promise<Session | null> {
  // Check if we have hash fragments in the URL (Supabase uses hash, not query)
  const hasHash = window.location.hash && window.location.hash.length > 1;
  
  if (hasHash) {
    // Parse hash to check if it's an auth callback
    const hashParams = new URLSearchParams(window.location.hash.substring(1));
    const type = hashParams.get('type');
    const accessToken = hashParams.get('access_token');
    
    // Only process if it looks like an auth callback
    if (type === 'recovery' || type === 'magiclink' || accessToken) {
      // Wait for next tick to ensure browser has parsed the hash
      await new Promise(resolve => setTimeout(resolve, 50));
      
      // Supabase automatically processes the hash when we call getSession()
      const { data, error } = await supabase.auth.getSession();
      
      if (error) {
        console.error('Error getting session from callback:', error);
        return null;
      }
      
      // Clear the hash from URL after processing for security
      // Preserve history.state so Vue Router's navigation state is not lost
      if (window.history.replaceState) {
        const cleanUrl = window.location.pathname + (window.location.search || '');
        window.history.replaceState(window.history.state, '', cleanUrl);
      }
      
      return data.session;
    }
  }
  
  // Fallback to regular session check (no hash present)
  return await getCurrentSession();
}

// Export the Supabase client for direct access if needed
export { supabase };
