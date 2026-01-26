import { ref, computed } from 'vue';

// Mock user data - replace with actual auth service in the future
const currentUser = ref({
  name: 'John Doe',
  email: 'john.doe@example.com',
  avatar: null as string | null,
  isAuthenticated: true,
});

export function useAuth() {
  const user = computed(() => currentUser.value);
  const isAuthenticated = computed(() => currentUser.value.isAuthenticated);

  const signOut = async () => {
    // TODO: Implement actual sign out logic
    console.log('Sign out triggered');
    // Mock sign out - replace with actual API call
    // currentUser.value.isAuthenticated = false;
    // router.push('/login');
  };

  const updateProfile = (updates: Partial<typeof currentUser.value>) => {
    currentUser.value = { ...currentUser.value, ...updates };
  };

  return {
    user,
    isAuthenticated,
    signOut,
    updateProfile,
  };
}
