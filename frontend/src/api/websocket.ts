import { io, Socket } from "socket.io-client";

let socket: Socket | null = null;

export const connectWebSocket = (token?: string) => {
  socket = io("/api/v1/ws/notify", {
    path: "/api/v1/ws/notify",
    transports: ["websocket"],
    auth: token ? { token } : undefined,
  });
  return socket;
};

export const getSocket = () => socket;
export const disconnectWebSocket = () => {
  if (socket) socket.disconnect();
  socket = null;
}; 