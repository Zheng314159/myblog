import React from "react";
import "./holoStyles.css";
import { useNotifications } from "@/components/HologramBanner/useNotifications.ts";

const typeStyles: Record<string, { color: string; speed: number }> = {
  system_notification: { color: "cyan", speed: 12 },
  challenge_me: { color: "lightred", speed: 18 },
  fund_me: { color: "yellow", speed: 15 },
  info: { color: "lightblue", speed: 14 },
  default: { color: "white", speed: 16 },
};

const HologramBanner: React.FC = () => {
  const { notifications } = useNotifications({
    maxCount: 10,
    initialFetchCount: 20,
  });

  if (notifications.length === 0) return null;

  const grouped = notifications.reduce((acc: Record<string, any[]>, n) => {
    if (!acc[n.type]) acc[n.type] = [];
    acc[n.type].push(n);
    return acc;
  }, {});

  return (
    <div className="holo-banner-container">
      <div className="holo-bg-grid" />
      <div className="holo-content">
        {Object.entries(grouped).map(([type, msgs], idx) => {
          const { color, speed } = typeStyles[type] || typeStyles.default;
          return (
            <div
              key={type}
              className="holo-line"
              style={{
                animationDelay: `${idx * 0.3}s`,
              }}
            >
              <div
                className="marquee"
                style={{
                  animationDuration: `${speed}s`,
                }}
              >
                {msgs.map((n, i) => (
                  <span
                    key={
                      n.data?.id?.toString().trim() ||
                      n.id?.toString().trim() ||
                      n.data?.title + "_" + n.data?.message ||
                      "msg-" + i
                    }
                    className="holo-message"
                    style={{
                      color,
                      textShadow: `0 0 5px ${color}, 0 0 10px ${color}`,
                    }}
                  >
                    <b>{n.data?.title || n.type}</b>:{" "}
                    {n.data?.message || n.data?.content}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default HologramBanner;
