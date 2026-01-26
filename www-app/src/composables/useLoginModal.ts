import { ref } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import { useRouter } from 'vue-router';

const showLoginModal = ref(false);

export function useLoginModal() {
  const authStore = useAuthStore();
  const router = useRouter();

  const open = () => {
    // Don't open login modal if user is authenticated
    if (authStore.isAuthenticated) {
      // Redirect to dashboard instead
      router.push({ name: 'dashboard' });
      return;
    }
    showLoginModal.value = true;
  };

  const close = () => {
    showLoginModal.value = false;
  };

  return {
    showLoginModal,
    open,
    close,
  };
}