// src/components/GlobalMessageProvider.tsx
import React, { createContext, useContext } from "react";
import { App, AppProps } from "antd";
import { setMessageApi, setNotificationApi } from "@/utils/message.ts";
import { GlobalMessageContextType } from "@/utils/message.ts";


export const GlobalMessageContext = createContext<GlobalMessageContextType | null>(
  null
);


export const GlobalMessageProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
    return (
    <App>
      <AppBridge>{children}</AppBridge>
    </App>
  );
};

// 这个组件用于桥接 App.useApp() 的返回值
const AppBridge: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const app = App.useApp();

  // 只初始化一次全局 api
  React.useEffect(() => {
    setMessageApi(app.message);
    setNotificationApi(app.notification);
  }, [app]);

  const contextValue: GlobalMessageContextType = {
    messageApi: app.message,
    notificationApi: app.notification,
  };

  return (
    <GlobalMessageContext.Provider value={contextValue}>
      {children}
    </GlobalMessageContext.Provider>
  );
};


export const useGlobalMessage = () => {
  const context = useContext(GlobalMessageContext);
  if (!context) {
    throw new Error(
      "useGlobalMessage must be used within a GlobalMessageProvider"
    );
  }
  return context;
};
