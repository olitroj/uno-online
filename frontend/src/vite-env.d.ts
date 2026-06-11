/// <reference types="vite/client" />

// Tell TypeScript that importing image files returns a URL string.
// Without this, TypeScript errors on:  import cat1 from '@/assets/cat1.PNG'
declare module '*.png' { const src: string; export default src }
declare module '*.PNG' { const src: string; export default src }
declare module '*.jpg' { const src: string; export default src }
declare module '*.svg' { const src: string; export default src }
