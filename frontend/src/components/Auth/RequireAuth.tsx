import React from "react";
import { useSelector } from "react-redux";
import { Navigate } from "react-router-dom";
import { RootState } from "../../app/store";
import { Spin } from "antd";

interface RequireAuthProps {
  children: React.ReactNode;
  role?: string;
}

const RequireAuth: React.FC<RequireAuthProps> = ({ children, role }) => {
  const { isAuthenticated, isLoading, userInfo } = useSelector((state: RootState) => state.user);
  
  // 如果正在加载，显示加载提示
  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '200px' 
      }}>
        <Spin size="large" />
      </div>
    );
  }
  
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (role && userInfo?.role !== role) return <Navigate to="/" replace />;
  return <>{children}</>;
};

export default RequireAuth; 