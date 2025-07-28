let ws: WebSocket | null = null;

const getWebSocketUrl = () => {
  const protocol =
    import.meta.env.VITE_WS_PROTOCOL ||
    (window.location.protocol === "https:" ? "wss" : "ws");
  const hostname = import.meta.env.VITE_WS_HOST || window.location.hostname;
  const port = import.meta.env.VITE_WS_PORT || "8000";
  const path = import.meta.env.VITE_WS_PATH || "/wss/ws";
  return `${protocol}://${hostname}:${port}${path}`;
};

export const connectWebSocket = (token?: string) => {
  if (
    ws &&
    ws.readyState !== WebSocket.CLOSED &&
    ws.readyState !== WebSocket.CLOSING
  ) {
    console.warn("WebSocket 已存在或正在关闭，跳过创建");
    return ws;
  }

  const url = getWebSocketUrl();
  const socket = new WebSocket(url);
  ws = socket;

  socket.addEventListener("open", () => {
    console.log("WebSocket连接已开启");
    if (token) {
      socket.send(JSON.stringify({ token }));
    }
    socket.send(JSON.stringify({ type: "subscribe", data: { channel: "home" } }));
  });

  ws.addEventListener("message", (event) => {
    console.log("收到消息:", event.data);
  });

  ws.addEventListener("error", (err) => {
    console.error("WebSocket 错误:", err);
  });

  ws.addEventListener("close", () => {
    console.warn("WebSocket 已关闭");
  });

  return ws;
};

export const getSocket = () => ws;

export const disconnectWebSocket = () => {
  if (ws) ws.close();
  ws = null;
};
