import { useEffect, useState, useRef } from "react";

import {
  getConfig,
  getNotifications,
} from "@/api/config.ts";
import { connectWebSocket, disconnectWebSocket } from "@/api/websocket.ts";

interface UseNotificationsOptions {
  maxCount?: number; // 最大保留通知条数，默认 5
  initialFetchCount?: number; // 首次拉取条数，默认 5
}

export function useNotifications(options: UseNotificationsOptions = {}) {
  const { maxCount = 5, initialFetchCount = 5 } = options;

  const [notifications, setNotifications] = useState<any[]>([]);
  const [taskStatus, setTaskStatus] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let wsCleanup: (() => void) | null = null;

    getConfig().then((cfg) => {
      const fetchEnabled = cfg?.enable_notification_fetch;
      const pushEnabled = cfg?.enable_notification_push;

      // 只拉取历史
      if (fetchEnabled && !pushEnabled) {
        fetchHistory();
        return;
      }

      // 只推送
      if (!fetchEnabled && pushEnabled) {
        initWebSocket();
        return;
      }

      // 拉取 + 推送
      if (fetchEnabled && pushEnabled) {
        fetchHistory();
        initWebSocket();
        return;
      }
    });

    return () => {
      if (wsCleanup) wsCleanup();
    };

    // 拉取历史
    function fetchHistory() {
      getNotifications(initialFetchCount).then((data) => {
        if (Array.isArray(data.notifications)) {
          const normalized = data.notifications.map((n: any) => ({
            type: "system_notification",
            data: n,
          }));
          setNotifications((prev) => mergeAndDedup(normalized, prev));
        }
      });
    }

    // 建立 WebSocket
    function initWebSocket() {
      const token = localStorage.getItem("access_token");
      const ws = connectWebSocket(token || undefined);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);

          if (msg.type) {
            setNotifications((prev) => mergeAndDedup([msg], prev));
          } else if (msg.type === "task_status") {
            setTaskStatus(msg.data);
          }
        } catch (e) {
          console.error("WebSocket message parse error", e);
        }
      };

      wsCleanup = () => {
        disconnectWebSocket();
        wsRef.current = null;
      };
    }

    // 合并 + 去重 + 截取最大条数
    function mergeAndDedup(newItems: any[], prev: any[]) {
      const all = [...newItems, ...prev];
      const map = new Map();

      for (const n of all) {
        const key =
          n.data?.id?.toString().trim() ||
          n.id?.toString().trim() ||
          (n.data?.title && n.data?.message
            ? n.data.title.toString().trim() +
              "_" +
              n.data.message.toString().trim()
            : undefined);
        if (!key) continue;
        if (!map.has(key)) {
          map.set(key, n);
        }
      }

      return Array.from(map.values()).slice(0, maxCount);
    }
  }, [maxCount, initialFetchCount]);

  return { notifications, taskStatus };
}
