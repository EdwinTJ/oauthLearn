export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
  compilerOptions: {
    // ...
    baseUrl: ".",
    paths: {
      "@/*": ["./src/*"],
    },
  },
};
