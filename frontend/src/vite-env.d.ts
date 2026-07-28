// src/vite-env.d.ts — Vite client types + CSS module declaration
/// <reference types="vite/client" />

declare module '*.css' {
  const styles: Record<string, string>;
  export default styles;
}
