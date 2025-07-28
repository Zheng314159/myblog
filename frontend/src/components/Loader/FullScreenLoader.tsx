import React from "react";
import { Spin } from "antd";

const FullScreenLoader: React.FC = () => {
  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#fff",
        zIndex: 9999,
      }}
    >
      <Spin size="large" tip="加载中...">
        <div style={{ marginTop: 16 }}>请稍候...</div>
      </Spin>
    </div>
  );
};

export default FullScreenLoader;
