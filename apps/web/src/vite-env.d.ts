/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_PROOFSTUDIO_API_BASE_URL?: string;
  readonly VITE_PROOFSTUDIO_AUTH_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
