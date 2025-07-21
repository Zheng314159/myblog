import React from "react";
import "./Banner.css";
import PhysicsDiagram from "./PhysicsDiagram";
import "katex/dist/katex.min.css";
import { BlockMath } from "react-katex";

const formula1 = String.raw`
  \begin{aligned}
    &m\ddot{r}-m\frac{v_{\theta }^2}{r}=F_r\\
    &v_{\theta }=h
  \end{aligned}
`;
const formula2 = String.raw`
  \begin{aligned}
    &-m\frac{v_{\theta }^2}{r}=F_r\\
    &v_{\theta }=h
  \end{aligned}
`;
const formula3 = String.raw`
  \begin{aligned}
    &m\ddot{r}-m\frac{h^2}{r}=-m\frac{h^2}{R}\\
    &v_{\theta }=h
  \end{aligned}
`;

const Banner: React.FC = () => (
  <div className="banner">
    <div className="banner-gradient-bg" />
    {/* 科技感物理氛围SVG点缀 */}
    <svg className="banner-bg-decor">
      {/* 彩色椭圆 */}
      <ellipse cx="15%" cy="80%" rx="180" ry="60" fill="#00eaff" opacity="0.18" />
      <ellipse cx="80%" cy="30%" rx="120" ry="40" fill="#ffb86c" opacity="0.13" />
      <ellipse cx="60%" cy="90%" rx="200" ry="80" fill="#aaffc3" opacity="0.12" />
      {/* 波浪线 */}
      <path d="M 0 180 Q 200 100 400 180 T 800 180 T 1200 180 T 1600 180 T 2000 180 T 2400 180 T 2800 180" stroke="#fff" strokeWidth="2" fill="none" opacity="0.08" />
      {/* 粒子点缀 */}
      <circle cx="10%" cy="20%" r="6" fill="#fff" opacity="0.12" />
      <circle cx="90%" cy="60%" r="8" fill="#fff" opacity="0.10" />
      <circle cx="50%" cy="10%" r="4" fill="#fff" opacity="0.10" />
      <circle cx="70%" cy="80%" r="5" fill="#fff" opacity="0.10" />
      <circle cx="30%" cy="60%" r="3" fill="#fff" opacity="0.10" />
    </svg>
    {/* 背景视频（优先） */}
    <video className="banner-bg-video" src="/banner.mp4" autoPlay loop muted playsInline poster="/banner.png" />
    {/* 背景图片（兜底） */}
    <div className="banner-bg-image" />
    {/* 半透明遮罩 */}
    <div className="banner-mask" />
    <div className="banner-content" style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
      <div className="banner-logo" style={{ width: 220, height: 220, overflow: "hidden", background: "#fff", borderRadius: "50%" }}>
        <PhysicsDiagram width={220} height={220} viewBox="0 0 2600 2000" />
      </div>
      <div className="banner-slogan">基于极坐标系的理论物理框架</div>
      {/* 右侧三组公式并排，移除白色背景方框 */}
      <div style={{ height: 220, display: "flex", alignItems: "center", justifyContent: "center", marginLeft: 24, gap: 32 }}>
        <BlockMath math={formula1} />
        <BlockMath math={formula2} />
        <BlockMath math={formula3} />
      </div>
    </div>
    {/* 物理示意图SVG（如需保留可取消注释） */}
    {/*
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: 0,
        width: "100%",
        height: "220px",
        pointerEvents: "none",
        zIndex: 0,
        overflow: "visible",
      }}
    >
      <PhysicsDiagram />
    </div>
    */}
    <div className="banner-cthulhu-waves">
      <svg width="100%" height="120" viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M0 80 Q 360 120 720 80 T 1440 80 V120 H0Z" fill="#1a3c3b" fillOpacity="0.5"/>
        <path d="M0 100 Q 360 60 720 100 T 1440 100 V120 H0Z" fill="#2c5364" fillOpacity="0.4"/>
        <path d="M0 110 Q 360 90 720 110 T 1440 110 V120 H0Z" fill="#203a43" fillOpacity="0.3"/>
      </svg>
    </div>
  </div>
);

export default Banner; 