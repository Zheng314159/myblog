import React, { useEffect, useRef, useState } from "react";
import "./Banner.css";
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

interface BannerProps {
  slogan?: string;
  formulas?: string[];
  scrollTargetId?: string;
}

export const Banner: React.FC<BannerProps> = ({
  slogan = "基于极坐标系的理论物理框架",
  formulas = [formula1, formula2, formula3],
  scrollTargetId = "next-section",
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [videoLoaded, setVideoLoaded] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVideoLoaded(true);
          observer.disconnect();
        }
      },
      { threshold: 0.3 }
    );
    const element = document.querySelector(".banner");
    if (element) observer.observe(element);
    return () => observer.disconnect();
  }, []);

  const [formulaIndex, setFormulaIndex] = useState(0);
  useEffect(() => {
    const timer = setInterval(() => {
      setFormulaIndex((i) => (i + 1) % formulas.length);
    }, 3000);
    return () => clearInterval(timer);
  }, [formulas]);



  return (
    <div className="banner relative">
      <div className="banner-gradient-bg" />

      <svg className="banner-bg-decor">
        <ellipse
          cx="15%"
          cy="80%"
          rx="180"
          ry="60"
          fill="#00eaff"
          opacity="0.18"
        />
        <ellipse
          cx="80%"
          cy="30%"
          rx="120"
          ry="40"
          fill="#ffb86c"
          opacity="0.13"
        />
        <ellipse
          cx="60%"
          cy="90%"
          rx="200"
          ry="80"
          fill="#aaffc3"
          opacity="0.12"
        />
        <path
          d="M 0 180 Q 200 100 400 180 T 800 180 T 1200 180 T 1600 180 T 2000 180 T 2400 180 T 2800 180"
          stroke="#fff"
          strokeWidth="2"
          fill="none"
          opacity="0.08"
        />
        <circle cx="10%" cy="20%" r="6" fill="#fff" opacity="0.12" />
        <circle cx="90%" cy="60%" r="8" fill="#fff" opacity="0.10" />
        <circle cx="50%" cy="10%" r="4" fill="#fff" opacity="0.10" />
        <circle cx="70%" cy="80%" r="5" fill="#fff" opacity="0.10" />
        <circle cx="30%" cy="60%" r="3" fill="#fff" opacity="0.10" />
      </svg>

      {videoLoaded && (
        <video
          ref={videoRef}
          className="banner-bg-video"
          src="/banner.mp4"
          autoPlay
          loop
          muted
          playsInline
          poster="/banner.png"
        />
      )}

      <div className="banner-bg-image" />
      <div className="banner-mask" />

      <div className="banner-content flex flex-col md:flex-row md:flex-nowrap items-center justify-between gap-6 px-4 md:px-12 w-full max-w-screen-xl mx-auto z-10">
        <div className="banner-logo-container hidden md:flex flex-shrink-0 w-[140px] h-[140px]">
          <img
            src="/favicon.svg"
            alt="Logo"
            className="w-full h-full object-contain"
          />
        </div>

        <div className="banner-slogan text-xl md:text-2xl font-bold text-center text-white max-w-md">
          {slogan}
        </div>
        <div className="banner-formula-box font-bold">
          <BlockMath math={`\\boldsymbol{${formulas[formulaIndex]}}`} />
        </div>
      </div>
    </div>
  );
};
