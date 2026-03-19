import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
<<<<<<< HEAD
    host: true,
  },
});
=======
    host: "localhost",
    port: 5300,
    strictPort: true,
  },
});

>>>>>>> upstream/main
