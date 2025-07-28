import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
// console.log("当前文件路径：", __filename);
// console.log("当前目录：", __dirname);
export default defineConfig(({ mode }) => {
  // 加载对应环境（development / production）的 env 文件
  const env = loadEnv(mode, process.cwd());
  console.log("当前工作目录：", process.cwd());
  console.log(`✅ 当前运行模式: ${mode}`);
  console.log("✅ 使用的环境变量:", env);
  
  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "src"), // 可选：支持 @ 作为路径别名
      },
    },
    server: {
      host: "0.0.0.0", // ✅ 监听所有网络接口（否则只能容器内访问）
      port: 3000,
      open: false,
      proxy: {
        "/api": {
          target: env.VITE_API_BASE_URL || "http://localhost:8000",
          changeOrigin: true,
        },
        "/uploads": {
          target: env.VITE_API_BASE_URL || "http://localhost:8000",
          changeOrigin: true,
        },
      },
    },
    define: {
      "import.meta.env.VITE_API_BASE_URL": JSON.stringify(
        env.VITE_API_BASE_URL
      ),
      // __API_BASE__: JSON.stringify(process.env.API_BASE),
    },
  };
});
