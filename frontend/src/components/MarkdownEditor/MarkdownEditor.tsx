import React from "react";
import MDEditor from "@uiw/react-md-editor";

interface Props {
  value: string;
  onChange: (v: string) => void;
}

const MarkdownEditor: React.FC<Props> = ({ value, onChange }) => (
  <div data-color-mode="light">
    <MDEditor value={value} onChange={onChange} height={400} />
  </div>
);

export default MarkdownEditor;