import { useLocation } from "react-router-dom";
import { useEffect } from "react";

export default function RouteLogger() {
  const location = useLocation();

  useEffect(() => {
    console.log("[路由变化]", location.pathname);
  }, [location.pathname]);

  return null;
}
