import React from "react";
import { useSelector } from "react-redux";
import { Navigate } from "react-router-dom";
import { RootState } from "../../app/store";

interface RequireAuthProps {
  children: React.ReactNode;
  role?: string;
}

const RequireAuth: React.FC<RequireAuthProps> = ({ children, role }) => {
  const { isAuthenticated, userInfo } = useSelector((state: RootState) => state.user);
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (role && userInfo?.role !== role) return <Navigate to="/" replace />;
  return <>{children}</>;
};

export default RequireAuth; 