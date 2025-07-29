// src/utils/showSessionExpiredModal.ts
import { Modal } from "antd";

export function showSessionExpiredModal() {
  Modal.warning({
    title: "登录状态已过期",
    content: "请重新登录后继续操作。",
    okText: "重新登录",
    closable: false,
    maskClosable: false,
    onOk: () => {
      window.location.href = "/login";
    },
  });
}
