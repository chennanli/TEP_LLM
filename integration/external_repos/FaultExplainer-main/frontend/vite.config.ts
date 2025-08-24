import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,  // Different from legacy (5173)
    headers: {
      "Cache-Control": "no-store",
    },
    proxy: {
      // Proxy API calls to integration unified control panel
      '/api': {
        target: 'http://localhost:9002',  // Integration control panel port
        changeOrigin: true,
        secure: false,
      }
    },
  },
});
