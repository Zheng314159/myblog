// src/utils/types.ts

import type { MessageInstance } from "antd/es/message/interface";
import type { NotificationInstance } from "antd/es/notification/interface";
import type { Modal } from "antd";

export interface GlobalUIContextType {
  messageApi: MessageInstance;
  notificationApi: NotificationInstance;
  modalApi: typeof Modal;
  showGlobalSpin: (content?: React.ReactNode) => void;
  hideGlobalSpin: () => void;
}
