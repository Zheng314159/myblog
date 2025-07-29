import { message } from "antd";

let lastToastTime = 0;
export function showTokenRefreshToast() {
  const now = Date.now();
  if (now - lastToastTime > 10_000) {
    // 每10秒最多提示一次
    message.success("Token 已自动续签");
    lastToastTime = now;
  }
}
