let ws: WebSocket | null = null;

export const connectWebSocket = (token?: string) => {
  const url = `ws://${window.location.hostname}:8000/api/v1/ws`;
  ws = new WebSocket(url);

  ws.onopen = () => {
    console.log('WS已连接');
    // 发送认证信息（如有token）
    ws?.send(JSON.stringify({ token }));
    // 订阅首页频道
    ws?.send(JSON.stringify({ type: "subscribe", data: { channel: "home" } }));
  };
  ws.onclose = (e) => { console.log('WS关闭:', e); };
  ws.onerror = (e) => { console.log('WS错误:', e); };

  return ws;
};

export const getSocket = () => ws;
export const disconnectWebSocket = () => {
  if (ws) ws.close();
  ws = null;
}; 