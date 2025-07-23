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
  const url = getWebSocketUrl();
  ws = new WebSocket(url);

  ws.onopen = () => {
    console.log("WS已连接:", url);
    if (token) {
      ws?.send(JSON.stringify({ token }));
    }
    ws?.send(JSON.stringify({ type: "subscribe", data: { channel: "home" } }));
  };

  ws.onclose = (e) => {
    console.log("WS关闭:", e);
  };
  ws.onerror = (e) => {
    console.log("WS错误:", e);
  };

  return ws;
};

export const getSocket = () => ws;

export const disconnectWebSocket = () => {
  if (ws) ws.close();
  ws = null;
};
