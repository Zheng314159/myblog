// src/types/antd-instances.d.ts

declare module "antd/es/message/interface" {
  import React from "react";

  export interface MessageArgsProps {
    content: React.ReactNode;
    duration?: number;
    type?: "info" | "success" | "error" | "warning" | "loading";
    onClose?: () => void;
    key?: string | number;
    className?: string;
    style?: React.CSSProperties;
  }

  export interface MessageInstance {
    open(args: MessageArgsProps): void;

    success(
      content: React.ReactNode,
      duration?: number,
      onClose?: () => void
    ): void;
    success(args: MessageArgsProps): void;

    error(
      content: React.ReactNode,
      duration?: number,
      onClose?: () => void
    ): void;
    error(args: MessageArgsProps): void;

    info(
      content: React.ReactNode,
      duration?: number,
      onClose?: () => void
    ): void;
    info(args: MessageArgsProps): void;

    warning(
      content: React.ReactNode,
      duration?: number,
      onClose?: () => void
    ): void;
    warning(args: MessageArgsProps): void;

    loading(
      content: React.ReactNode,
      duration?: number,
      onClose?: () => void
    ): void;
    loading(args: MessageArgsProps): void;

    destroy(key?: string | number): void;
  }
}


declare module "antd/es/notification/interface" {
  export interface NotificationArgsProps {
    message: React.ReactNode;
    description?: React.ReactNode;
    btn?: React.ReactNode;
    key?: string | number;
    onClose?: () => void;
    duration?: number | null;
    icon?: React.ReactNode;
    placement?: "topLeft" | "topRight" | "bottomLeft" | "bottomRight";
    style?: React.CSSProperties;
    className?: string;
  }

  export interface NotificationInstance {
    open: (args: NotificationArgsProps) => void;
    info: (args: NotificationArgsProps) => void;
    success: (args: NotificationArgsProps) => void;
    error: (args: NotificationArgsProps) => void;
    warning: (args: NotificationArgsProps) => void;
    destroy: (key?: string | number) => void;
  }
}
