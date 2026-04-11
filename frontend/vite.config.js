import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";
const proxyPaths = [
    "/process",
    "/runs",
    "/topics",
    "/source-summary",
    "/jira-read",
    "/confluence-read",
    "/health",
];
export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, __dirname, "");
    const apiProxyTarget = env.VITE_API_PROXY_TARGET || "http://localhost:8000";
    const usePolling = env.VITE_USE_POLLING === "true";
    return {
        plugins: [react()],
        resolve: {
            alias: [
                {
                    find: /^@\//,
                    replacement: `${fileURLToPath(new URL("./src/", import.meta.url))}`,
                },
            ],
        },
        server: {
            host: "0.0.0.0",
            port: 5173,
            strictPort: true,
            hmr: {
                clientPort: 5173,
            },
            watch: usePolling
                ? {
                    usePolling: true,
                    interval: 300,
                }
                : undefined,
            proxy: Object.fromEntries(proxyPaths.map((route) => [
                route,
                {
                    target: apiProxyTarget,
                    changeOrigin: true,
                },
            ])),
        },
    };
});
