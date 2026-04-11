import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
var proxyPaths = [
    "/process",
    "/runs",
    "/topics",
    "/source-summary",
    "/jira-read",
    "/confluence-read",
    "/health",
];
export default defineConfig(function (_a) {
    var mode = _a.mode;
    var env = loadEnv(mode, __dirname, "");
    var apiProxyTarget = env.VITE_API_PROXY_TARGET || "http://localhost:8000";
    var usePolling = env.VITE_USE_POLLING === "true";
    return {
        plugins: [react()],
        resolve: {
            alias: [
                {
                    find: /^@\//,
                    replacement: "".concat(path.resolve(__dirname, "./src"), "/"),
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
            proxy: Object.fromEntries(proxyPaths.map(function (route) { return [
                route,
                {
                    target: apiProxyTarget,
                    changeOrigin: true,
                },
            ]; })),
        },
    };
});
