import React from "react";
import "./Banner.css";

const Banner: React.FC = () => (
  <div className="banner">
    <div className="banner-logo">
      <img src="/logo192.png" alt="Logo" />
    </div>
    <div className="banner-slogan">fastapi博客系统</div>
    <div className="banner-ad">[广告位招租]</div>
  </div>
);

export default Banner; 