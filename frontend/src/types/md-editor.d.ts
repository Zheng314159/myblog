declare module "@uiw/react-md-editor" {
  import * as React from "react";

  interface MDEditorProps {
    value?: string;
    onChange?: (value?: string) => void;
    height?: number;
    preview?: "edit" | "preview" | "live";
    textareaProps?: React.TextareaHTMLAttributes<HTMLTextAreaElement>;
    [key: string]: any;
  }

  const MDEditor: React.FC<MDEditorProps>;
  export default MDEditor;
}
