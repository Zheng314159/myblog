// src/pages/Demo.tsx
import React from "react";
import { useGlobalUI } from "@/hooks/useGlobalUI";

const Demo = () => {
  const {
    messageApi,
    notificationApi,
    modalApi,
    showGlobalSpin,
    hideGlobalSpin,
  } = useGlobalUI();

  const handleClick = async () => {
    showGlobalSpin("处理中...");
    setTimeout(() => {
      hideGlobalSpin();
      messageApi.success("处理成功！");
      notificationApi.info({ message: "通知", description: "已完成操作。" });
    }, 2000);
  };

  return <button onClick={handleClick}>点击测试全局 UI</button>;
};

export default Demo;
