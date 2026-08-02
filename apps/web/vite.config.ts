import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// PS-013 Demo UI Shell / Review Room frontend.
//
// The API base URL is resolved at runtime from VITE_PROOFSTUDIO_API_BASE_URL
// (see src/api.ts) and falls back to http://127.0.0.1:8000 so the dev shell
// works against a local `uvicorn proofstudio.api.app:app` with no config.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
  },
});
