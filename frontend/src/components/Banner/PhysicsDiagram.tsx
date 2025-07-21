import React from "react";

interface PhysicsDiagramProps {
  width?: number | string;
  height?: number | string;
  viewBox?: string;
}

const PhysicsDiagram: React.FC<PhysicsDiagramProps> = ({
  width = "100%",
  height = "100%",
  viewBox = "0 0 2600 2000",
}) => (
  <svg
    width={width}
    height={height}
    viewBox={viewBox}
    preserveAspectRatio="xMidYMid meet"
    style={{ display: "block" }}
  >
    {/* 大圆 */}
    <circle cx="1600" cy="1000" r="1000" fill="none" stroke="black" strokeWidth="6" />
    {/* 椭圆 */}
    <ellipse cx="1000" cy="1000" rx="1000" ry="800" fill="none" stroke="#f0c" strokeWidth="6" opacity="0.7" />
    {/* 主要辅助线 */}
    <line x1="1000" y1="200" x2="1600" y2="1000" stroke="black" strokeWidth="2" />
    <line x1="1000" y1="200" x2="1000" y2="1000" stroke="black" strokeWidth="2" />
    <line x1="1000" y1="1800" x2="1600" y2="1000" stroke="black" strokeWidth="2" />
    <line x1="0" y1="1000" x2="2600" y2="1000" stroke="black" strokeWidth="2" />
    {/* 标注点 */}
    <circle cx="0" cy="1000" r="16" fill="#0f0" />
    <circle cx="600" cy="1000" r="16" fill="#0f0" />
    <circle cx="1600" cy="1000" r="16" fill="#0f0" />
    <circle cx="2000" cy="1000" r="16" fill="#0f0" />
    <circle cx="2600" cy="1000" r="16" fill="#0f0" />
    <circle cx="1000" cy="200" r="16" fill="#0f0" />
    <circle cx="1000" cy="1800" r="16" fill="#0f0" />
    {/* 字母标注 */}
    <text x="0" y="990" fontSize="48" fill="#0f0" fontWeight="bold">A</text>
    <text x="980" y="180" fontSize="48" fill="#0f0" fontWeight="bold">C</text>
    <text x="1600" y="990" fontSize="48" fill="#0f0" fontWeight="bold">O</text>
    <text x="2600" y="990" fontSize="48" fill="#0f0" fontWeight="bold">F</text>
    <text x="980" y="1840" fontSize="48" fill="#0f0" fontWeight="bold">D</text>
    <text x="2000" y="990" fontSize="48" fill="#0f0" fontWeight="bold">B</text>
    <text x="600" y="990" fontSize="48" fill="#0f0" fontWeight="bold">E</text>
    {/* 主要长度标注 */}
    <text x="300" y="1040" fontSize="36" fill="black">600</text>
    <text x="1400" y="1040" fontSize="36" fill="black">600</text>
    <text x="1800" y="1040" fontSize="36" fill="black">400</text>
    <text x="2400" y="1040" fontSize="36" fill="black">600</text>
    <text x="1000" y="600" fontSize="36" fill="black">800</text>
    <text x="700" y="1040" fontSize="36" fill="black">400</text>
    <text x="1400" y="700" fontSize="36" fill="black">1000</text>
    {/* 眼睛图案可用emoji或svg图标替代 */}
    <text x="1600" y="1040" fontSize="48" fill="black" opacity="0.5">👁️</text>
  </svg>
);

export default PhysicsDiagram; 