// src/components/GlobalUIProvider.tsx
import React, { createContext, useContext, useState, useEffect } from "react";
import { App, Modal, Spin } from "antd";

import type { GlobalUIContextType } from "@/utils/types";
import { LoadingOutlined } from "@ant-design/icons";

export const GlobalUIContext = createContext<GlobalUIContextType | null>(null);

export const GlobalUIProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <App>
      <AppBridge>{children}</AppBridge>
    </App>
  );
};

const AppBridge: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const app = App.useApp();
  const [spinning, setSpinning] = useState(false);
  const [spinContent, setSpinContent] = useState<React.ReactNode>("加载中...");

  // 避免在 messageApi 未准备好时渲染 Provider
  const ready = !!(app.message && app.notification);

  useEffect(() => {
    if (!ready) return;
    // 可以在这里 log 一下 app.message 来确认是否拿到了
    // console.log("App.useApp ready:", app.message);
  }, [ready]);
  const contextValue: GlobalUIContextType = {
    messageApi: app.message,
    notificationApi: app.notification,
    modalApi: Modal,
    showGlobalSpin: (content) => {
      if (content) setSpinContent(content);
      setSpinning(true);
    },
    hideGlobalSpin: () => setSpinning(false),
  };

  return (
    <GlobalUIContext.Provider value={contextValue}>
      {spinning && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            zIndex: 2000,
            width: "100vw",
            height: "100vh",
            backgroundColor: "rgba(255,255,255,0.6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            pointerEvents: "none",
          }}
        >
          <Spin
            spinning={true}
            indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />}
            tip={spinContent}
            size="large"
          />
        </div>
      )}
      {children}
    </GlobalUIContext.Provider>
  );
};


