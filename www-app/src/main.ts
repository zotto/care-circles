import { createApp } from 'vue';
import { createPinia } from 'pinia';
import router from './router';
import App from './App.vue';
import './style.css';
import { useAuthStore } from './stores/authStore';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

// Initialize auth store before mounting
const authStore = useAuthStore();
authStore.initialize().then(() => {
  app.mount('#app');
}).catch((error) => {
  console.error('Failed to initialize auth:', error);
  // Mount app anyway to show login page
  app.mount('#app');
});
