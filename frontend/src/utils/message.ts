import type { MessageInstance } from "antd/es/message/interface";
import type { NotificationInstance } from "antd/es/notification/interface";

let messageApi: MessageInstance | null = null;
let notificationApi: NotificationInstance | null = null;

export function setMessageApi(instance: MessageInstance) {
  messageApi = instance;
}

export function setNotificationApi(instance: NotificationInstance) {
  notificationApi = instance;
}

export const globalMessage = {
  success(content: string, duration?: number) {
    messageApi?.success({ content, duration });
  },
  error(content: string, duration?: number) {
    messageApi?.error({ content, duration });
  },
  info(content: string, duration?: number) {
    messageApi?.info({ content, duration });
  },
  warning(content: string, duration?: number) {
    messageApi?.warning({ content, duration });
  },
  loading(content: string, duration?: number) {
    return messageApi?.loading({ content, duration });
  },
};

export const globalNotification = {
  success: (args: Parameters<NotificationInstance["success"]>[0]) => {
    notificationApi?.success(args);
  },
  error: (args: Parameters<NotificationInstance["error"]>[0]) => {
    notificationApi?.error(args);
  },
  info: (args: Parameters<NotificationInstance["info"]>[0]) => {
    notificationApi?.info(args);
  },
  warning: (args: Parameters<NotificationInstance["warning"]>[0]) => {
    notificationApi?.warning(args);
  },
};
export  type GlobalMessageContextType = {
    messageApi: MessageInstance;
    notificationApi: NotificationInstance;
    };